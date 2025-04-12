from django.urls import path

from .views import (UserInformationView, UserRegistrationView,
                    UserRewardsListView, UserRewardRequestView)


urlpatterns = [
    path(
        "register/", UserRegistrationView.as_view(), name="user-registration"
    ),
    path("profile/", UserInformationView.as_view(), name="user-information"),
    path("rewards/", UserRewardsListView.as_view(), name="user-rewards"),
    path(
        "rewards/request/",
        UserRewardRequestView.as_view(),
        name="user-request-reward",
    ),
]
