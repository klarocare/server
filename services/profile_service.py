from fastapi import HTTPException, status

from models.user import UserProfile, UserCredentials
from schemas.profile_schema import ProfileRequest

class ProfileService:

    @staticmethod
    async def create(request: ProfileRequest, credentials: UserCredentials):
        if await credentials.get_user():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already created"
            )
        user = UserProfile(
            credentials_id=credentials.id,
            username=request.username,
            caretaker_name=request.caretaker_name,
            language=request.language
            )
        await user.insert()
        return user