from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    В идеале для разделения логики мы можем (и, наверное, даже должны)
    использовать отдельное django-приложение внутри данного проекта, например,
    users, в котором определяем модели с нужными нам полями. Это позволит нам
    независимо управлять аккаунтами пользователей и логикой приложения.
    """

    coins = models.IntegerField(
        default=0, blank=True, verbose_name="Количество монет у пользователя"
    )
