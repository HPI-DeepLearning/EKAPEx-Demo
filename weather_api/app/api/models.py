from pydantic import BaseModel
from typing import List

class TimeRange(BaseModel):
    """Time range model for API requests."""
    baseTime: int
    validTime: List[int]

    class Config:
        schema_extra = {
            "example": {
                "baseTime": 1609459200,
                "validTime": [1609459200, 1609462800]
            }
        }