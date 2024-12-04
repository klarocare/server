from typing import List

from pydantic import BaseModel, Field


class Patient(BaseModel):
    """
    Patient model
    """
    name: str = Field(description="Name of the patient.")
    challenges: List[str] = Field(description="List of challenges the caregiver has.")


class Caregiver(BaseModel):
    """
    Caregiver relative model
    """
    name: str = Field(description="Name of caregiver relative.")
    patient: Patient = Field(description="Name of the care task.")
