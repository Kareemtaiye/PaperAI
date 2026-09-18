from pydantic import BaseModel, ConfigDict


class ErrorResponse(BaseModel):
    status: str
    message: str
    code: int

    model_config = ConfigDict(from_attributes=True)
