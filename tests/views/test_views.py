import json

import pytest
from django.core.cache import cache as django_cache
from redis import Redis

from rewards.views import (UserInformationView, UserRegistrationView,
                           UserRewardRequestView, UserRewardsListView)


@pytest.mark.usefixtures("celery_app")
@pytest.mark.django_db(transaction=True, reset_sequences=True)
class TestViews:
    def test_user_registration(self, rf, user_data):
        request = rf.post("/api/register/", data=user_data)
        user_reg_view = UserRegistrationView.as_view()
        response = user_reg_view(request)
        assert response.status_code == 201

        response_content = response.render().content.decode()
        assert json.loads(response_content) == {
            "message": "Пользователь создан"
        }

    def test_user_profile(self, rf, user_for_tests, access_token):
        request = rf.get(
            "api/profile/", headers={"Authorization": f"Bearer {access_token}"}
        )
        profile_view = UserInformationView.as_view()
        response = profile_view(request)
        response_body = json.loads(response.render().content.decode())
        ethalon = {
            "username": "testuser",
            "email": "test@user.com",
            "coins": 0,
        }

        assert response_body == ethalon
