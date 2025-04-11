from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ScheduledReward


@receiver(post_save, sender=ScheduledReward)
def schedule_reward_runner_signal(sender, instance, created, **kwargs):
    if created:
        instance.schedule_reward()
