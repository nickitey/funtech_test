from datetime import datetime, timedelta, timezone

from django.core.cache import cache
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ScheduledReward
from .serializers import (UserInfoSerializer, UserRegistrationSerializer,
                          UserRewardsSerializer)


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
            return Response(
                {"message": "Пользователь создан"},
                status=status.HTTP_201_CREATED,
            )
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


class UserRewardRequestView(APIView):
    """
    Дополнительно: класс-представление для запроса пользователем награды,
    но не чаще раза в сутки.
    Варианта два: добавить в модель User поле вроде "requested_reward",
    где хранить булево значение, и каждый раз, как пользователь запросит
    награду, проверять значение этого поля во view, если оно False, то обновлять
    его на True и вешать в Celery задачу на изменение статуса обратно через сутки.
    Но поскольку у нас уже есть Redis, который выступает брокером для Celery,
    мы можем добавлять по id пользователя в кэш на сутки информацию, когда
    пользователь запрашивает награду, и проверять: если в кэше есть запись,
    то награды не будет, если записи в кэше нет - то получит награду, а в кэш
    добавится на сутки запрет на добавление ему награды.
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        cache_key = f"user_{user.pk}_requested_reward"
        user_requested_reward = cache.get(cache_key)
        if user_requested_reward:
            return Response(
                {
                    "user": f"{user.username}",
                    "reward request status": "Not Allowed",
                    "description": "Вы уже запрашивали награду в течение "
                    "последних суток.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        ScheduledReward.objects.create(
            user=user,
            amount=5,
            execute_at=datetime.now(tz=timezone.utc) + timedelta(minutes=5),
        )
        cache_timeout = 60 * 60 * 24
        cache.set(cache_key, True, cache_timeout)
        return Response(
            {
                "user": f"{user.username}",
                "reward request status": "Success",
                "description": "Награда запрошена и будет зачислена в течение "
                "пяти минут.",
            },
            status=status.HTTP_202_ACCEPTED,
        )
