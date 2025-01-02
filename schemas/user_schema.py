from typing import List

from pydantic import BaseModel, Field


class Caregiver(BaseModel):
    """
    Caregiver relative model
    """
    name: str = Field(description="Name of caregiver relative.")
    patient_name: str = Field(description="Name of the care task.")
    challenges: str = Field(description="Challenges the caregiver has.")
