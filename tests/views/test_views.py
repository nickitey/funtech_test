import json
import pickle
from datetime import datetime, timezone

import pytest

from rewards.models import ScheduledReward
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

    def test_user_awards(self, rf, user_for_tests, access_token):
        [
            ScheduledReward.objects.create(
                user=user_for_tests,
                amount=amount,
                execute_at=datetime.now(tz=timezone.utc),
            )
            for amount in (5, 7, 9)
        ]

        request = rf.get(
            "api/rewards/", headers={"Authorization": f"Bearer {access_token}"}
        )
        awards_view = UserRewardsListView.as_view()
        response = awards_view(request)
        response_body = json.loads(response.render().content.decode())

        assert len(response_body["rewards"]) == 3
        assert (
            sum(reward["amount"] for reward in response_body["rewards"]) == 21
        )

    def test_user_award_request(self, rf, user_for_tests, access_token):
        # Убедимся, что до начала теста у пользователя нет монет.
        assert user_for_tests.coins == 0
        request = rf.post(
            "api/rewards/request/",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        award_request_view = UserRewardRequestView.as_view()
        response = award_request_view(request)
        response_body = json.loads(response.render().content.decode())
        ethalon = {
            "user": "testuser",
            "reward request status": "Success",
            "description": "Награда запрошена и будет зачислена в течение пяти минут.",
        }
        assert response_body == ethalon

        user_for_tests.refresh_from_db()
        # После выполнения запроса у пользователя становится 5 монет.
        assert user_for_tests.coins == 5

    def test_forbid_second_user_award_request_(
        self, rf, user_for_tests, access_token, redis_client
    ):
        assert user_for_tests.coins == 0
        request = rf.post(
            "api/rewards/request/",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        award_request_view = UserRewardRequestView.as_view()
        award_request_view(request)
        response = award_request_view(request)
        response_body = json.loads(response.render().content.decode())

        ethalon = {
            "user": "testuser",
            "reward request status": "Not Allowed",
            "description": "Вы уже запрашивали награду в течение последних суток.",
        }
        assert response_body == ethalon

        # Убедимся, что в кэше действительно есть запись, связанная с нашим
        # пользователем, который запросил награду
        with redis_client as redis:
            cache_key = f"rewards:1:user_{user_for_tests.pk}_requested_reward"
            content = redis.get(cache_key)
            assert pickle.loads(content) is True

            # Кроме того, убедимся, что срок жизни указанной записи немногим
            # меньше 86400 секунд (60 сек * 59 мин * 24 ч)
            assert redis.ttl(cache_key) > 60 * 59 * 24
