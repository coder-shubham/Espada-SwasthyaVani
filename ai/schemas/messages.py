from pydantic import BaseModel
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime


class RequestType(str, Enum):
    TEXT = "text"
    AUDIO = "audio"


class MLRequest(BaseModel):
    request_id: str
    request_type: RequestType
    content: str
    model: str
    user_id: Optional[str] = None
    timestamp: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None


class MLResponse(BaseModel):
    request_id: str
    result: Dict[str, Any]
    model: str
    timestamp: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None


class MLError(BaseModel):
    request_id: str
    error: str
    details: Optional[str] = None
    timestamp: datetime = datetime.utcnow()
