from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class LocationType(Enum):
    PHARMACY = "pharmacy"
    MEDICAL_SUPPLY_STORE = "medical supply store"
    HARDWARE_STORE = "hardware store"


class LocationQuery(BaseModel):
    query: List[LocationType] = Field(description="Query that can be used in Google maps to search. Includes the type of places needed to be searched.")

    def concat(self):
        return ", ".join(query.value for query in self.query)