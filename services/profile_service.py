from models.user import User
from schemas.profile_schema import UpdateProfileRequest


class ProfileService:

    @staticmethod
    def update_user(request: UpdateProfileRequest, user: User) -> User:
        if request.username is not None:
            user.username = request.username
        if request.caretaker_name is not None:
            user.caretaker_name = request.caretaker_name
        if request.language is not None:
            user.language = request.language
        
        user.save()
        return user