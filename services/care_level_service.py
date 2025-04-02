from schemas.care_level_schema import CareAssessmentSchema, CareEstimateSchema


class CareLevelService:

    def get_care_benefits(schema: CareAssessmentSchema) -> CareEstimateSchema:
        level = CareLevelService._get_care_level(schema)
        benefits = CareLevelService._get_benefit_list(level)
        return CareEstimateSchema(level=level, benefits=benefits)

    @staticmethod
    def _get_care_level(schema: CareAssessmentSchema):
        score = 0

        if schema.is_mobility_restricted: score += 1
        if not schema.can_walk_short_distance: score += 1
        if schema.mobilirt_issue_reason == 'Stroke': score += 2
        elif schema.mobilirt_issue_reason: score += 1

        if not schema.can_manage_daily_tasks_alone: score += 2

        score += schema.needs_assistance_with_personal_care.get_score()
        score += schema.has_memory_issues.get_score()
        score += schema.can_express_needs_clearly.get_score()

        if score <= 2: return 'L1'
        if score <= 4: return 'L2'
        if score <= 6: return 'L3'
        if score <= 8: return 'L4'
        return 'L5'
    
    @staticmethod
    def _get_benefit_list(level: str):
        match level:
            case 'L1':
                return [
                'Care money as high as \$750',
                'Basic caregiver funds',
                ]
            case 'L2':
                return [
                'Care money as high as \$1250',
                'Caregiver funds',
                'Home adaptation assistance',
                'Monthly respite care',
                ]
            case 'L3':
                return [
                'Care money as high as \$1550',
                'Extended caregiver support',
                'Home adaptation funds',
                'Monthly respite care',
                'Transportation assistance',
                ]
            case _:
                return [
                'Care money as high as \$2000',
                'Full caregiver support package',
                'Comprehensive home adaptation',
                'Weekly respite care',
                'Transportation assistance',
                'Medical equipment coverage',
                ]
    
    @staticmethod
    def _get_benefit_amount(level: str):

        match level:
            case 'L1':
                return '\$750'
            case 'L2':
                return '\$1250'
            case 'L3':
                return '\$1550'
            case 'L4':
                return '\$1550'
            case 'L5':
                return '\$2000'
            case _:
                return '\$0'