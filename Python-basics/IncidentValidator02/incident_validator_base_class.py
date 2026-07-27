from pydantic import BaseModel
from datetime import datetime
from enums_class import Severity


class Incident(BaseModel):
    service: str
    severity: Severity
    error: str
    timestamp: datetime