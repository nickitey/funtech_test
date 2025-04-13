import json

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
