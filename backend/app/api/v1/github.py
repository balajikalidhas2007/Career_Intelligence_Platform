"""GitHub repository sync API."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.dependencies import get_current_user
from app.models.evidence import Evidence
from app.models.user import User
from app.schemas.github import GitHubRepoEvidence, GitHubSyncResponse
from app.services.github_service import (
    GitHubRepo,
    fetch_readme,
    fetch_user_repos,
    get_github_token,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/github", tags=["github"])


@router.post("/sync", response_model=GitHubSyncResponse)
async def sync_github_repos(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Sync GitHub repositories as evidence items.

    Fetches repos from GitHub using the stored OAuth token,
    creates/updates Evidence records, and avoids duplicates.
    """
    # Get the user's GitHub token
    try:
        github_token = await get_github_token(db, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Fetch repos from GitHub
    try:
        repos = await fetch_user_repos(github_token)
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception:
        logger.exception("Failed to fetch GitHub repos")
        raise HTTPException(status_code=502, detail="Failed to communicate with GitHub")

    # Load existing github evidence for this user (keyed by source_reference)
    existing_result = await db.execute(
        select(Evidence).where(
            Evidence.user_id == current_user.id,
            Evidence.source_type == "github",
        )
    )
    existing_by_ref: dict[str, Evidence] = {
        ev.source_reference: ev for ev in existing_result.scalars().all() if ev.source_reference
    }

    created_count = 0
    updated_count = 0
    response_repos: list[GitHubRepoEvidence] = []

    for repo in repos:
        source_ref = f"github:{repo.repo_id}"

        # Fetch README for non-fork repos (skip forks to save API calls)
        readme = None
        if not repo.is_fork:
            readme = await fetch_readme(github_token, repo.full_name)

        metadata = {
            "repo_id": repo.repo_id,
            "full_name": repo.full_name,
            "language": repo.language,
            "topics": repo.topics,
            "stargazers_count": repo.stargazers_count,
            "forks_count": repo.forks_count,
            "is_fork": repo.is_fork,
        }
        if readme:
            metadata["readme_preview"] = readme[:2000]

        description = repo.description or ""
        if repo.language:
            description += f" [Language: {repo.language}]"
        if repo.topics:
            description += f" [Topics: {', '.join(repo.topics)}]"

        is_new = False
        if source_ref in existing_by_ref:
            # Update existing evidence
            ev = existing_by_ref[source_ref]
            ev.title = repo.name
            ev.description = description or None
            ev.metadata_ = metadata
            ev.is_stale = False
            updated_count += 1
        else:
            # Create new evidence
            ev = Evidence(
                user_id=current_user.id,
                source_type="github",
                source_reference=source_ref,
                title=repo.name,
                description=description or None,
                metadata_=metadata,
            )
            db.add(ev)
            created_count += 1
            is_new = True

        await db.flush()

        response_repos.append(
            GitHubRepoEvidence(
                evidence_id=ev.id,
                repo_name=repo.name,
                full_name=repo.full_name,
                html_url=repo.html_url,
                description=repo.description,
                language=repo.language,
                topics=repo.topics,
                stargazers_count=repo.stargazers_count,
                forks_count=repo.forks_count,
                is_new=is_new,
                created_at=ev.created_at,
            )
        )

    # Mark any existing evidence NOT in the current sync as stale
    synced_refs = {f"github:{r.repo_id}" for r in repos}
    for ref, ev in existing_by_ref.items():
        if ref not in synced_refs:
            ev.is_stale = True

    return GitHubSyncResponse(
        synced=len(response_repos),
        created=created_count,
        updated=updated_count,
        repos=response_repos,
    )


@router.get("/evidence", response_model=list[GitHubRepoEvidence])
async def list_github_evidence(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """List existing GitHub repository evidence for the current user."""
    result = await db.execute(
        select(Evidence)
        .where(
            Evidence.user_id == current_user.id,
            Evidence.source_type == "github",
        )
        .order_by(Evidence.created_at.desc())
    )
    evidences = result.scalars().all()

    return [
        GitHubRepoEvidence(
            evidence_id=ev.id,
            repo_name=ev.title,
            full_name=ev.metadata_.get("full_name", ev.title) if ev.metadata_ else ev.title,
            html_url=f"https://github.com/{ev.metadata_.get('full_name', '')}" if ev.metadata_ else "",
            description=ev.description,
            language=ev.metadata_.get("language") if ev.metadata_ else None,
            topics=ev.metadata_.get("topics", []) if ev.metadata_ else [],
            stargazers_count=ev.metadata_.get("stargazers_count", 0) if ev.metadata_ else 0,
            forks_count=ev.metadata_.get("forks_count", 0) if ev.metadata_ else 0,
            is_new=False,
            created_at=ev.created_at,
        )
        for ev in evidences
    ]
