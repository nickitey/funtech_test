import json

from django.conf import settings
from redis import Redis
import pytest
from pytest_django.fixtures import rf

from rewards.extensions import CustomTokenObtainPairView


@pytest.fixture
def user_data():
    return {
        "username": "testuser",
        "email": "test@user.com",
        "password": "1234",
    }


@pytest.fixture
def access_token(user_for_tests, user_data, rf):
    request = rf.post("/api/token/", data=user_data)
    token_view = CustomTokenObtainPairView.as_view()
    response = token_view(request)
    response_body = json.loads(response.render().content.decode())
    return response_body["access"]


@pytest.fixture
def redis_client():
    redis_client = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            username=settings.REDIS_USER,
            password=settings.REDIS_PASSWORD
    )
    try:
        # Мы не ожидаем каких-то ошибок, которые приведут к аварийному завершению
        # тестов, но для большего контроля в любом случае, даже если возникнет
        # непредвиденное исключение, мы в finally закроем соединение.
        yield redis_client
        # Очистка кэша после теста как гарантия идемпотентности стартовых условий.
        redis_client.flushall()
    finally:
        # По большому счету, после остановки контейнера при завершении тестов
        # соединение и так будет закрыто. Но "явное лучше, чем неявное" (С).
        redis_client.close()
