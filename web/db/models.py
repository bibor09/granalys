from pydantic import BaseModel
from datetime import datetime

class Analysis(BaseModel):
    user: str
    repo: str
    branch: str
    gd_id: str
    created: datetime
    statistics_all: dict[str, dict[str, str]] = None