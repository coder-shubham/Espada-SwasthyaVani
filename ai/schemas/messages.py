from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
import json


class RequestType(str, Enum):
    TEXT = "text"
    AUDIO = "audio"


@dataclass
class MLRequest:
    request_id: str
    request_type: RequestType
    content: str
    language: str
    sender: str
    timestamp: int
    timestampInLong: int
    type: Optional[str] = None
    model: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    isFinished: Optional[bool] = False

    def to_string(self) -> str:
        return json.dumps(asdict(self), default=str)


class MLResponse(BaseModel):
    request_id: str
    content: str
    model: Optional[str] = None
    user_id: Optional[str] = None
    request_type: RequestType
    # timestamp: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None


class MLError(BaseModel):
    request_id: str
    error: str
    details: Optional[str] = None
    timestamp: datetime = datetime.utcnow()
