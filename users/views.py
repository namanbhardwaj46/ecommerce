from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from .exceptions import UserAlreadyExistsError, InvalidCredentialsError
from .serializers import (UserSignupSerializer, UserResponseSerializer,
                          UserSerializer, UserLoginSerializer)
from .services import LoginService, TokenService
from .models import User

# Create your views here.

class ListUserView(APIView):
    def get(self, request):
        try:
            users = User.objects.all()
            user_serializer = UserSerializer(users, many=True)
            return Response(user_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserSignUpView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        user_serializer = UserSignupSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)

        try:
            user = user_serializer.save()
        except UserAlreadyExistsError as exc:
            return Response({"email": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        tokens = TokenService.generate_token_pair(user)

        return Response(
            {
                "message": "User created successfully!",
                "user": UserResponseSerializer(user).data,
                "access": tokens["access"],
                "refresh": tokens["refresh"],
            },
            status=status.HTTP_201_CREATED
        )

class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_login_serializer = UserLoginSerializer(data=request.data)

        user_login_serializer.is_valid(raise_exception=True)

        try:
            user = LoginService.login_user(
                email=user_login_serializer.validated_data["email"],
                password=user_login_serializer.validated_data["password"],
                request=request,
            )

        except InvalidCredentialsError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_401_UNAUTHORIZED)

        tokens = TokenService.generate_token_pair(user)

        return Response(
            {
                "message": "Login successful!",
                "user": UserResponseSerializer(user).data,
                "access": tokens["access"],
                "refresh": tokens["refresh"],
            },
            status=status.HTTP_200_OK,
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            UserSerializer(request.user).data,
            status=status.HTTP_200_OK,
        )

class UserDetailView(APIView):
    def get_object(self, pk):
        # Helper method to retrieve a user object by its primary key (pk).
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None

    def get(self, request, pk):
        # Retrieve details of a specific user.
        user = self.get_object(pk)
        if not user:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        user_serializer = UserResponseSerializer(user)
        return Response(user_serializer.data, status=status.HTTP_200_OK)

    # def patch(self, request, pk):
    #     # Update the details of a specific user partially or fully.
    #     user = self.get_object(pk)
    #     if not user:
    #         return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    #     user_serializer = UserSerializer(user, data=request.data, partial=True)
    #     if user_serializer.is_valid():
    #         user_serializer.save()
    #         return Response(user_serializer.data, status=status.HTTP_200_OK)
    #     return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        # Delete a specific user.
        user = self.get_object(pk)
        if not user:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
