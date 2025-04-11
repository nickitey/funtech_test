from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Пакет simplejwt покрывает только работу с аутентификацией, но не регистрацию
    нового пользователя. Поэтому нам нужен отдельный эндпоинт и сериализатор
    для создания нового пользователя.
    """
    password = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user_model = self.Meta.model
        new_user = user_model.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return new_user


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "email",
            "coins"
        )
