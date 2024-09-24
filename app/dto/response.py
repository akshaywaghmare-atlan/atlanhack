from typing import Any, Optional

from pydantic import BaseModel


class BaseResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None
