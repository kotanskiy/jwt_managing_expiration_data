class ProfileError(Exception):
    message: str = ""


class UserHasNotPermissionError(ProfileError):
    message = "Permission denied"


class UserNotFoundError(ProfileError):
    message = "User does not exists"
