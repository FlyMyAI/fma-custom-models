from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DeployedModelData(BaseModel):
    model_name: str
    predict_endpoint: str
    logs_link: Optional[str] = None


class HardwareLogs(BaseModel):
    link: str
    created_at: datetime
