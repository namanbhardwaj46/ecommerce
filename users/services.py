from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .exceptions import UserAlreadyExistsError, InvalidCredentialsError


User = get_user_model()


class UserService:
    """
        Application service responsible for User-related business operations.
    """

    @staticmethod
    @transaction.atomic
    def register_user(*, email, password, first_name="", last_name=""):
        """
            Register a new user.

            Responsibilities:
            - Normalize email according to application policy.
            - Prevent duplicate email registration.
            - Hash the password through Django.
            - Persist the User atomically.
        """

        email = User.objects.normalize_email(email).strip()

        if User.objects.filter(email=email).exists():
            raise UserAlreadyExistsError(
                "A user with this email already exists."
            )

        try:
            user = User.objects.create_user(
                email=email,
                first_name=first_name.strip(),
                last_name=last_name.strip(),
                password=password,
            )

        except IntegrityError as exc:
            # Protect against concurrent registration requests
            # racing between the exists() check and INSERT.
            raise UserAlreadyExistsError(
                "A user with this email already exists."
            ) from exc

        return user

class LoginService:
    """
        Application service responsible for user authentication.
    """

    @staticmethod
    def login_user(*, email, password, request=None):
        """
            Authenticate an existing user using email and password.

            Returns:
                User instance

            Raises:
                InvalidCredentialsError:
                    If authentication fails.
        """

        email = User.objects.normalize_email(email).strip()

        user = authenticate(username=email, password=password, request=request)

        if user is None:
            raise InvalidCredentialsError(
                "Invalid email or password."
            )

        return user


class TokenService:
    """
        Application service responsible for JWT generation.
    """

    @staticmethod
    def _add_custom_claims(token, user):
        """
            Add application-specific claims to the JWT.
        """

        token["user_id"] = user.id
        token["email"] = user.email
        token["first_name"] = user.first_name
        token["last_name"] = user.last_name
        token["is_verified"] = user.is_verified
        token["roles"] = list(user.roles.values_list("name", flat=True))

        return token

    @classmethod
    def get_refresh_token(cls, user):
        """
            Create a refresh token with custom claims.
        """

        refresh = RefreshToken.for_user(user)

        return cls._add_custom_claims(refresh, user,)

    @classmethod
    def generate_token_pair(cls, user):
        """
            Generate access and refresh tokens for a user.
        """

        refresh = cls.get_refresh_token(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }