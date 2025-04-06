from models.user import User

async def run():
    async for user in User.find_all():
        if not hasattr(user, "care_level"):
            user.care_level = None
            await user.save()
        if not hasattr(user, "caretaker_relationship"):
            user.caretaker_relationship = None
            await user.save()
