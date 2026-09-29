"""GitHub API service for fetching user repositories.

Uses the stored encrypted OAuth token from AuthAccount.
"""

from __future__ import annotations

import base64
import logging
import uuid
from dataclasses import dataclass, field

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth_account import AuthAccount
from app.utils.security import decrypt_github_token

logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"


@dataclass
class GitHubRepo:
    """Lightweight representation of a GitHub repository."""

    repo_id: int
    name: str
    full_name: str
    html_url: str
    description: str | None = None
    language: str | None = None
    topics: list[str] = field(default_factory=list)
    stargazers_count: int = 0
    forks_count: int = 0
    is_fork: bool = False
    readme_text: str | None = None


async def get_github_token(db: AsyncSession, user_id: uuid.UUID) -> str:
    """Retrieve and decrypt the user's GitHub OAuth token."""
    result = await db.execute(
        select(AuthAccount).where(
            AuthAccount.user_id == user_id,
            AuthAccount.provider == "github",
        )
    )
    auth_account = result.scalar_one_or_none()

    if not auth_account or not auth_account.access_token_encrypted:
        raise ValueError("No GitHub account linked or token missing")

    return decrypt_github_token(auth_account.access_token_encrypted)


async def fetch_user_repos(github_token: str, max_repos: int = 50) -> list[GitHubRepo]:
    """Fetch the authenticated user's repositories from GitHub API."""
    repos: list[GitHubRepo] = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        headers = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        page = 1
        while len(repos) < max_repos:
            resp = await client.get(
                f"{GITHUB_API_BASE}/user/repos",
                headers=headers,
                params={
                    "sort": "updated",
                    "direction": "desc",
                    "per_page": min(30, max_repos - len(repos)),
                    "page": page,
                    "type": "owner",
                },
            )

            if resp.status_code == 401:
                raise ValueError("GitHub token is invalid or expired")
            if resp.status_code == 403:
                raise ValueError("GitHub API rate limit exceeded or forbidden")
            resp.raise_for_status()

            data = resp.json()
            if not data:
                break

            for item in data:
                repos.append(
                    GitHubRepo(
                        repo_id=item["id"],
                        name=item["name"],
                        full_name=item["full_name"],
                        html_url=item["html_url"],
                        description=item.get("description"),
                        language=item.get("language"),
                        topics=item.get("topics", []),
                        stargazers_count=item.get("stargazers_count", 0),
                        forks_count=item.get("forks_count", 0),
                        is_fork=item.get("fork", False),
                    )
                )

            page += 1

    return repos


async def fetch_readme(github_token: str, full_name: str) -> str | None:
    """Fetch the README content for a repository. Returns None if unavailable."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        headers = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json",
        }
        try:
            resp = await client.get(
                f"{GITHUB_API_BASE}/repos/{full_name}/readme",
                headers=headers,
            )
            if resp.status_code != 200:
                return None

            data = resp.json()
            content = data.get("content", "")
            encoding = data.get("encoding", "")

            if encoding == "base64" and content:
                try:
                    return base64.b64decode(content).decode("utf-8", errors="replace")[:5000]
                except Exception:
                    return None
        except httpx.HTTPError:
            return None

    return None
