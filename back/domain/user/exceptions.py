class UserError(Exception):
    pass


class UserHasNotPermissionError(UserError):
    message = "Permission denied"


class UserNotFoundError(UserError):
    message = "User does not exists"
