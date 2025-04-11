from django.urls import include, path

from .views import *  # Так делать нельзя и мы обязательно от этого избавимся.
                      # Позже.


urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="user-registration")
]
