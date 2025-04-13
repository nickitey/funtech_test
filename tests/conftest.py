import pytest
from django.contrib.auth import get_user_model

from apirewards.celery import app


# Эта фикстура позволит использовать реальное приложение Celery, написанное
# для проекта.
# Данное приложение незамедлительно выполняет созданные задачи, что позволяет
# в тестах не быть связанным с Celery-worker
@pytest.fixture(scope="class")
def celery_app(request):
    app.conf.update(CELERY_TASK_ALWAYS_EAGER=True)
    return app


@pytest.fixture
def user_for_tests():
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="testuser", email="test@user.com", password="1234"
    )
    user.save()
    return user
