from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class Frequency(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    NOT_APPLICABLE = "notApplicable"
    NEVER = "never"
    RARELY = "rarely"
    FREQUENTLY = "frequently"

    def get_score(self) -> int:
        return {
            self.DAILY: 3,
            self.WEEKLY: 2,
            self.MONTHLY: 1,
            self.NOT_APPLICABLE: 0,
            self.NEVER: 0,
            self.RARELY: 1,
            self.FREQUENTLY: 2
        }[self]


class CareLevel(Enum):
    PG0 = "PG 0"
    PG1 = "PG 1"
    PG2 = "PG 2"
    PG3 = "PG 3"
    PG4 = "PG 4"
    PG5 = "PG 5"


class MobilitySchema(BaseModel):
    short_distance: int = Field(ge=0, le=3)
    transfer: int = Field(ge=0, le=3)


class CognitionSchema(BaseModel):
    recognize_people: int = Field(ge=0, le=3)
    remember_events: int = Field(ge=0, le=3)


class BehaviorSchema(BaseModel):
    anxious_aggressive: Frequency
    resist_care: Frequency


class SelfCareSchema(BaseModel):
    personal_hygiene: int = Field(ge=0, le=3)
    toilet_hygiene: int = Field(ge=0, le=3)


class HealthDemandsSchema(BaseModel):
    medication_needs: Frequency
    uses_medical_aids: Frequency


class EverydayLifeSchema(BaseModel):
    manage_daily_routine: int = Field(ge=0, le=3)
    plan_adapt_day: int = Field(ge=0, le=3)


class CareLevelRequestSchema(BaseModel):
    mobility: MobilitySchema
    cognition: CognitionSchema
    behavior: BehaviorSchema
    self_care: SelfCareSchema
    health_demands: HealthDemandsSchema
    everyday_life: EverydayLifeSchema


class CareLevelResponseSchema(BaseModel):
    level: CareLevel
    benefits: list[str]
