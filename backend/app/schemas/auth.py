from typing import Optional
import uuid
from pydantic import BaseModel

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: uuid.UUID
    email: Optional[str]
    display_name: str
    avatar_url: Optional[str]

    model_config = {"from_attributes": True}
