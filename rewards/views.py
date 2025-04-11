from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegistrationSerializer, UserInfoSerializer, UserRewardsSerializer


class UserRegistrationView(APIView):
    """
    Пакет simplejwt покрывает только работу с аутентификацией, но не регистрацию
    нового пользователя. Поэтому нам нужен отдельный эндпоинт и сериализатор
    для создания нового пользователя.
    Ручка будет отвечать на POST-запросы, будет доступна для всех (очевидно,
    для создания пользователя не нужна авторизация).
    """
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Пользователь создан"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserInformationView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = UserInfoSerializer(request.user)
        return Response(serializer.data)


class UserRewardsListView(APIView):
    """
    Класс-представление для получения пользователем списка его наград.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = UserRewardsSerializer(request.user)
        return Response(serializer.data)
