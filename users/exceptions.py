class UserServiceError(Exception):
    """Base exception for UserService."""

class UserAlreadyExistsError(UserServiceError):
    """Custom exception for user already exists errors"""
    pass

class InvalidCredentialsError(UserServiceError):
    """Raised when user login credentials are invalid."""
    pass
