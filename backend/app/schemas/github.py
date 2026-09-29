"""Pydantic schemas for GitHub sync responses."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class GitHubRepoEvidence(BaseModel):
    """A single GitHub repository evidence item."""

    evidence_id: uuid.UUID
    repo_name: str
    full_name: str
    html_url: str
    description: Optional[str]
    language: Optional[str]
    topics: list[str]
    stargazers_count: int
    forks_count: int
    is_new: bool  # True if created during this sync, False if updated
    created_at: datetime


class GitHubSyncResponse(BaseModel):
    """Response after syncing GitHub repositories."""

    synced: int
    created: int
    updated: int
    repos: list[GitHubRepoEvidence]
