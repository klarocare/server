from enum import Enum
from typing import List
from pydantic import BaseModel


class Frequency(Enum):
    NEVER = "never"
    SOMETIMES = "sometimes"
    ALWAYS = "always"

    def get_score(self):
        match self:
            case Frequency.NEVER:
                return 0
            case Frequency.SOMETIMES:
                return 1
            case _:
                return 2


class CareAssessmentSchema(BaseModel):
    is_mobility_restricted: bool 
    can_walk_short_distance: bool
    mobilirt_issue_reason: str
    can_manage_daily_tasks_alone: bool
    needs_assistance_with_personal_care: Frequency
    has_memory_issues: Frequency
    can_express_needs_clearly: Frequency


class CareEstimateSchema(BaseModel):
    level: str
    benefits: List[str]
