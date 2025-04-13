from datetime import datetime, timedelta, timezone
from typing import Type

import pytest
from django.db import models

from rewards.models import RewardLog, ScheduledReward, User

from .conftest import _TestModelAttrs


class TestUserModel(_TestModelAttrs):

    @property
    def model(self) -> Type[User]:
        return User

    def test_meta_data(self) -> None:
        meta = self.model._meta
        print(meta.verbose_name)
        assert meta.verbose_name == "пользователь"
        assert meta.verbose_name_plural == "пользователи"

    @pytest.mark.parametrize(
        "field, type, params",
        [
            ("coins", models.IntegerField, {
                "null": False,
                "blank": True,
                "verbose_name": "Количество монет у пользователя",
            }
             )
        ],
        ids=[f"Тест поля 'coins'"]
    )
    def test_model_attrs(self, field, type, params) -> None:
        super().test_model_attrs(field, type, params)


class TestScheduleRewardModel(_TestModelAttrs):
    @property
    def model(self) -> Type[ScheduledReward]:
        return ScheduledReward

    def test_meta_data(self) -> None:
        meta = self.model._meta
        assert meta.verbose_name == "Задание о присвоении награды"
        assert meta.verbose_name_plural == "Задания о присвоении награды"

    @pytest.mark.parametrize(
        "field, type, params",
        [
            ("user", models.ForeignKey, {
                "related_model": User,
                "verbose_name": "Пользователь, запросивший награду",
            },
             ),
            ("amount", models.IntegerField, {
                "null": False,
                "blank": True,
                "default": 0,
                "verbose_name": "Количество монет к начислению"},
             ),
            ("execute_at", models.DateTimeField, {
                "null": False,
                "verbose_name": "Планируемое время начисления награды",
            },
             ),
        ],
        ids=[f"Тест поля '{field}'" for field in [
            "user",
            "amount",
            "execute_at",
        ]
             ],
    )
    def test_model_attrs(self, field, type, params) -> None:
        super().test_model_attrs(field, type, params)

    @pytest.mark.usefixtures("celery_app")
    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def test_schedule_reward(self, user_for_tests):
        self.model.objects.create(
            user=user_for_tests,
            amount=5,
            execute_at=datetime.now(tz=timezone.utc)
        )
        user_for_tests.refresh_from_db()
        assert user_for_tests.coins == 5


class TestRewardLogModel(_TestModelAttrs):
    @property
    def model(self) -> Type[RewardLog]:
        return RewardLog

    def test_meta_data(self) -> None:
        meta = self.model._meta
        assert meta.verbose_name == "Запись о присвоении награды"
        assert meta.verbose_name_plural == "Записи о присвоении награды"

    @pytest.mark.parametrize(
        "field, type, params",
        [
            ("user", models.ForeignKey, {
                "related_model": User,
                "verbose_name": "Пользователь, получивший награду",
            },
             ),
            ("amount", models.IntegerField, {
                "null": False,
                "blank": True,
                "default": 0,
                "verbose_name": "Количество начисленных монет"},
             ),
            ("given_at", models.DateTimeField, {
                "null": False,
                "auto_now_add": True,
                "verbose_name": "Фактическое время начисления награды",
            },
             ),
        ],
        ids=[f"Тест поля '{field}'" for field in [
            "user",
            "amount",
            "given_at",
        ]
             ],
    )
    def test_model_attrs(self, field, type, params) -> None:
        super().test_model_attrs(field, type, params)

    @pytest.mark.usefixtures("celery_app")
    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def test_schedule_reward(self, user_for_tests):
        scheduler_reward = ScheduledReward(
            user=user_for_tests,
            amount=5,
            execute_at=datetime.now(tz=timezone.utc)
        )
        scheduler_reward.save()

        rewards_log = self.model.objects.first()
        assert (rewards_log.given_at - scheduler_reward.execute_at) < timedelta(seconds=1)
