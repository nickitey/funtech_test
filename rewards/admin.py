from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import RewardLog, ScheduledReward


@admin.register(get_user_model())
class AdminUser(admin.ModelAdmin):
    list_display = ("pk", "username", "email", "is_active", "coins")
    list_editable = ("coins",)


@admin.register(ScheduledReward)
class AdminScheduleReward(admin.ModelAdmin):
    list_display = ("user", "amount", "execute_at")


@admin.register(RewardLog)
class AdminRewardLog(admin.ModelAdmin):
    list_display = ("user", "amount", "given_at")
