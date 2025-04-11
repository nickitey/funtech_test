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

    def __str__(self):
        return self.username


class ScheduledReward(models.Model):
    user = models.ForeignKey(
        to=get_user_model(),  # Несмотря на то, что модель пользователя
                              # определена у нас тут же, не стоит наступать
                              # на грабли и ссылаться непосредственно на объект
                              # модели. Django предоставляет невероятно удобный
                              # интерфейс для того, чтобы в любом месте кода
                              # получать текущий объект модели пользователя,
                              # не будучи привязанным к одной конкретной модели
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Пользователь, запросивший награду",
        related_name="scheduled_rewards"
    )
    amount = models.IntegerField(
        default=0, blank=True, verbose_name="Количество монет к начислению"
    )
    execute_at = models.DateTimeField(
        verbose_name="Планируемое время начисления награды"
    )

    def schedule_reward(self):
        """
        Обычно все импорты находятся вверху модуля и выполняются при его
        инициализации.
        Но с Django и Celery не все так просто в силу архитектуры фреймворка.
        Задачи, связанные с ORM-объектами, могут использовать классы моделей,
        в класах моделей могут использоваться эти задачи, и все это вызывает
        циклический импорт и сопутствующие ему проблемы.
        PEP8 не возбраняется использовать тот факт, что импорты в Python
        осуществляются в рантайме, поэтому импорт во время работы функции/метода -
        вполне себе рабочая практика. Из-за того, что код внутри функций
        не выполняется при импорте модуля, циклического импорта не происходит.
        Минусы у этого решения тоже есть, но плюсы сильно перевешивают.
        """
        from .tasks import run_scheduled_reward_task

        run_scheduled_reward_task.apply_async(
            args=(self.pk,),
            eta=self.execute_at
        )



    def __str__(self):
        return (f"Награда пользователю {self.user} в размере {self.amount} "
                f"монет, запланированная к выдаче {self.execute_at}")


class RewardLog(models.Model):
    user = models.ForeignKey(
        to=get_user_model(),
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Пользователь, получивший награду",
        related_name='rewards'
    )
    amount = models.IntegerField(
        default=0, blank=True, verbose_name="Количество начисленных монет"
    )
    given_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Фактическое время начисления награды"
    )

    def __str__(self):
        return (f"Награда пользователю {self.user} в размере {self.amount} "
                f"монет, выданная {self.given_at}")
