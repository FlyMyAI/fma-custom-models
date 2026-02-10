from datetime import datetime

from pydantic import BaseModel


class DeployedModelData(BaseModel):
    model_name: str
    predict_endpoint: str


class HardwareLogs(BaseModel):
    link: str
    created_at: datetime
