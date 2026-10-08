# from rest_framework import serializers
#
# from users.models import User
#
#
# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = '__all__'


from .models import User
from django.contrib.auth import password_validation
from rest_framework import serializers

from .exceptions import UserAlreadyExistsError
from .services import UserService, TokenService


# User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "is_verified",]
        read_only_fields = ["id", "is_verified",]


class UserSignupSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, min_length=8,
        style={
            "input_type": "password"
        },
    )

    password_confirm = serializers.CharField(write_only=True,
        style={
            "input_type": "password"
        },
    )

    class Meta:
        model = User

        fields = [
            "first_name",
            "last_name",
            "email",
            "password",
            "password_confirm",
        ]

        extra_kwargs = {
            "email": {
                "required": True
            },
            "first_name": {
                "required": True
            },
            "last_name": {
                "required": True
            },
        }

    def validate_email(self, value):
        """
            Preserve local-part casing.

            We do NOT use .lower().
        """

        value = User.objects.normalize_email(value.strip())

        # Exact lookup intentionally used.
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )

        return value

    def validate(self, attrs):

        password = attrs["password"]
        password_confirm = attrs["password_confirm"]

        if password != password_confirm:
            raise serializers.ValidationError({
                "password_confirm": "Passwords do not match."
            })

        # Validate against Django's configured password validators.
        user = User(
            email=attrs.get("email"),
            first_name=attrs.get("first_name", ""),
            last_name=attrs.get("last_name", ""),
        )

        password_validation.validate_password(
            password,
            user=user,
        )

        return attrs

    def create(self, validated_data):

        validated_data.pop(
            "password_confirm"
        )

        try:
            return UserService.register_user(
                **validated_data
            )

        except UserAlreadyExistsError as exc:
            raise serializers.ValidationError(
                {
                    "email": str(exc)
                }
            ) from exc


class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "is_verified",
        ]
        read_only_fields = [
            "id",
            "email",
            "is_verified",
        ]


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, trim_whitespace=False)
