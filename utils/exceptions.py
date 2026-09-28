class AppError(Exception):
    """Base class ng lahat ng business errors."""


class EmailAlreadyExistsError(AppError):
    pass

class InvalidCredentialsError(AppError):
    pass

class UserNotFoundError(AppError):
    pass

class ProjectNotFoundError(AppError):
    pass

class NotProjectOwnerError(AppError):
    pass

class TaskNotFoundError(AppError):
    pass

class InvalidAssigneeError(AppError):
    pass