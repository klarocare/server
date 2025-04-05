from schemas.care_level_schema import (
    CareLevelRequestSchema,
    CareLevelResponseSchema,
    CareLevel,
    Frequency
)


class CareLevelService:
    @staticmethod
    def calculate_care_level(request: CareLevelRequestSchema) -> CareLevelResponseSchema:
        # Calculate average scores for each module
        mobility_score = CareLevelService._calculate_mobility_score(request.mobility)
        cognition_score = CareLevelService._calculate_cognition_score(request.cognition)
        behavior_score = CareLevelService._calculate_behavior_score(request.behavior)
        self_care_score = CareLevelService._calculate_self_care_score(request.self_care)
        health_demands_score = CareLevelService._calculate_health_demands_score(request.health_demands)
        everyday_life_score = CareLevelService._calculate_everyday_life_score(request.everyday_life)

        # Apply module weights
        weighted_mobility = mobility_score * 10  # M1: 10%
        weighted_m2 = max(cognition_score, behavior_score) * 15  # M2: 15% (higher of M2a or M2b)
        weighted_self_care = self_care_score * 40  # M3: 40%
        weighted_health = health_demands_score * 20  # M4: 20%
        weighted_everyday = everyday_life_score * 15  # M5: 15%

        # Calculate total weighted score (max 300)
        total_weighted_score = (
            weighted_mobility +
            weighted_m2 +
            weighted_self_care +
            weighted_health +
            weighted_everyday
        )

        # Calculate final score (0-100)
        final_score = (total_weighted_score / 300) * 100

        # Determine care level based on final score
        care_level = CareLevelService._determine_care_level(final_score)
        
        # Get benefits based on care level
        benefits = CareLevelService._get_benefits(care_level)

        return CareLevelResponseSchema(
            level=care_level,
            score=final_score,
            benefits=benefits
        )

    @staticmethod
    def _calculate_mobility_score(mobility) -> float:
        """Calculate average score for mobility module (M1)"""
        return (mobility.short_distance + mobility.transfer) / 2

    @staticmethod
    def _calculate_cognition_score(cognition) -> float:
        """Calculate average score for cognition module (M2a)"""
        return (cognition.recognize_people + cognition.remember_events) / 2

    @staticmethod
    def _calculate_behavior_score(behavior) -> float:
        """Calculate average score for behavior module (M2b)"""
        anxious_score = Frequency(behavior.anxious_aggressive).get_score()
        resist_score = Frequency(behavior.resist_care).get_score()

        return (anxious_score + resist_score) / 2

    @staticmethod
    def _calculate_self_care_score(self_care) -> float:
        """Calculate average score for self-care module (M3)"""
        return (self_care.personal_hygiene + self_care.toilet_hygiene) / 2

    @staticmethod
    def _calculate_health_demands_score(health) -> float:
        """Calculate average score for health demands module (M4)"""
        medication_score = Frequency(health.medication_needs).get_score()
        aids_score = Frequency(health.uses_medical_aids).get_score()

        return (medication_score + aids_score) / 2

    @staticmethod
    def _calculate_everyday_life_score(everyday) -> float:
        """Calculate average score for everyday life module (M5)"""
        return (everyday.manage_daily_routine + everyday.plan_adapt_day) / 2

    @staticmethod
    def _determine_care_level(score: float) -> CareLevel:
        """Determine care level based on final score"""
        if score < 12.5:
            return CareLevel.PG0
        elif score < 27:
            return CareLevel.PG1
        elif score < 47.5:
            return CareLevel.PG2
        elif score < 70:
            return CareLevel.PG3
        elif score < 90:
            return CareLevel.PG4
        else:
            return CareLevel.PG5

    @staticmethod
    def _get_benefits(level: CareLevel) -> list[str]:
        """Get list of benefits based on care level"""
        benefits_map = {
            CareLevel.PG0: [
                "Basic care consultation",
                "Prevention services"
            ],
            CareLevel.PG1: [
                "Care allowance up to €316/month",
                "Basic care services",
                "Relief amount of €125/month"
            ],
            CareLevel.PG2: [
                "Care allowance up to €545/month",
                "Extended care services",
                "Relief amount of €125/month",
                "Respite care",
                "Day and night care"
            ],
            CareLevel.PG3: [
                "Care allowance up to €728/month",
                "Comprehensive care services",
                "Relief amount of €125/month",
                "Extended respite care",
                "Day and night care",
                "Care aids and home modifications"
            ],
            CareLevel.PG4: [
                "Care allowance up to €901/month",
                "Intensive care services",
                "Relief amount of €125/month",
                "Full respite care package",
                "Day and night care",
                "Care aids and home modifications",
                "Additional support for caregivers"
            ],
            CareLevel.PG5: [
                "Care allowance up to €1,015/month",
                "Maximum care services",
                "Relief amount of €125/month",
                "Full care support package",
                "Extended day and night care",
                "Comprehensive care aids",
                "Maximum support for caregivers",
                "Special hardship provisions"
            ]
        }
        return benefits_map[level]