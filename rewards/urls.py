from django.urls import path

from .views import *  # Так делать нельзя и мы обязательно от этого избавимся.
                      # Позже.


urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="user-registration"),
    path("profile/", UserInformationView.as_view(), name="user-information"),
    path("rewards/", UserRewardsListView.as_view(), name="user-rewards")
]
