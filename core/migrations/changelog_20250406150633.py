from models.user import User

async def run():
    async for user in User.find_all():
        needs_update = False

        # Check using model_dump to ensure it's not auto-set by the model
        user_data = user.model_dump(exclude_unset=True)

        if "care_level" not in user_data:
            user.care_level = None
            needs_update = True

        if "caretaker_relationship" not in user_data:
            user.caretaker_relationship = None
            needs_update = True

        if needs_update:
            await user.save()
