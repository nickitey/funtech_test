from apirewards.celery import app

from .models import RewardLog, ScheduledReward


@app.task
def run_scheduled_reward_task(scheduled_reward_id):
    try:
        scheduled_reward = ScheduledReward.objects.get(id=scheduled_reward_id)
    except ScheduledReward.DoesNotExist:
        raise Exception(
            f"ScheduledReward с ID {scheduled_reward_id} не найден"
        )
    else:
        # Обновляем количество наград пользователя
        user = scheduled_reward.user
        amount = scheduled_reward.amount
        user.coins = user.coins + amount
        user.save()

        # Создаем запись, что пользователю начислена награда
        RewardLog.objects.create(user=user, amount=amount)
        # В модели RewardLog определено, что при создании инстанса поле given_at
        # заполняется текущим временем и датой автоматически.
