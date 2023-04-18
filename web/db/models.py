from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Analysis(BaseModel):
    user: str
    repo: str
    branch: str
    gd_id: str
    created: datetime
    statistics_all: str = None