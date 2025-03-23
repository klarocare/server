from models.user import User

async def run():
    async for user in User.find_all():
        if not hasattr(user, "is_verified"):
            user.is_verified = True
            user.verification_token = None
            user.verification_token_expires = None
            await user.save()
