"""Aggregate router for all API v1 endpoints."""

from fastapi import APIRouter

api_v1_router = APIRouter()


@api_v1_router.get("/status", tags=["system"])
async def api_status() -> dict[str, str]:
    """API v1 status check."""
    return {"api": "v1", "status": "operational"}
