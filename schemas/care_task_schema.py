from enum import Enum
from typing import List
from pydantic import BaseModel, Field

from schemas.user_schema import Caregiver


class GenerateRequest(BaseModel):
    caregiver: Caregiver

class TaskCategory(Enum):
    MOBILITY = "mobility"
    COGNITIVE_SKILLS = "cognitive skills"
    BEHANIORAL_WELLNESS = "behavioral wellness"
    SELF_CARE_ABILITIES = "self-care abilities"
    TREATMENT_MANAGEMENT = "treatment management"
    SOCIAL_ENGAGEMENT = "social engagement"
    BUREAUCACY = "bureaucracy"


class CareTask(BaseModel):
    """
    Care task model. It contains the information about a care task. 
    """
    name: str = Field(description="Name of the care task.")
    assignee: str = Field(description="Assignee of the task, the person who should do the task.")
    duration: int = Field(description="Approximate duration of the task in minutes.")
    category: TaskCategory = Field(description="Category of the task, what does this task aim to address.")
    motivation: str = Field(description="Brief motivation on why this task is important, what happens when the will do and what could happen when don't.")
    instructions: List[str] = Field(description="Step-by-step guide for the caregiver. Avoid specifying special materials; instead, suggest ordinary items like a photo album rather than a memory card game. Be specific in the instructions and provide examples, especially for open-ended questions.")


class CareTaskList(BaseModel):
    """
    Care task list model. Contains list of care tasks.
    """
    care_tasks: List[CareTask] = Field(description="The list of the care tasks.")