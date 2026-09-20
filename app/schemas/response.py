from typing import Optional

from pydantic import BaseModel, ConfigDict


class ErrorResponse(BaseModel):
    status: str
    message: str
    code: int
    details: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)
