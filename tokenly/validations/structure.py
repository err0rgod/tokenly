"""
Validation module for checking the structural integrity of user credentials.
Ensures that usernames and passwords meet specific length and complexity requirements.
"""

from tokenly.model.models import userdata
from functools import wraps

def validate_creds_structure(func):
    """
    Decorator to validate the structure of user credentials (username and password).

    Validates:
    - Presence of username and password.
    - Username length (3-15 chars) and alphanumeric content.
    - Password complexity:
        - Minimum 8 characters.
        - At least one uppercase letter.
        - At least one lowercase letter.
        - At least one digit.
        - At least one special character.

    Args:
        func (Callable): The function to be decorated.

    Returns:
        Callable: The wrapped function with validation logic.

    Raises:
        ValueError: If any validation rule is violated.
    """
    @wraps(func)
    def wrapper(User: userdata, *args, **kwargs):
        """
        Internal wrapper that performs credential validation.

        Args:
            User (userdata): User object containing credentials to validate.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Any: The result of the decorated function if validation passes.
        """
        if not User.user_name or not User.password:
            raise ValueError("Username and password are required")
            
        if len(User.user_name) < 3 or len(User.user_name) > 15:
            raise ValueError("Username must be between 3 and 15 characters")
            
        if not User.user_name.isalnum():
            raise ValueError("Username must be alphanumeric; no special characters allowed")

        if len(User.password) < 8:
            raise ValueError("Password must be at least 8 characters long")
            
        if not any(char.isupper() for char in User.password):
            raise ValueError("Password must contain at least one uppercase letter")
            
        if not any(char.islower() for char in User.password):
            raise ValueError("Password must contain at least one lowercase letter")
            
        if not any(char.isdigit() for char in User.password):
            raise ValueError("Password must contain at least one digit")
            
        if not any(char in "!@#$%^&*()-_=+[]{}|;:,.<>?/" for char in User.password):
            raise ValueError("Password must contain at least one special character")

        return func(User, *args, **kwargs)
    return wrapper