from pydantic import BaseModel, ValidationError
from incident_validator_base_class import Incident

data={
    "service": "payroll-service",
    "severity": "high",
    "error": "Duplicate payroll generated",
    "timestamp": "2026-07-21T10:30:00"
}


try:
    incident = Incident.model_validate(data)
    print(incident)
except ValidationError as e:
    print(e)