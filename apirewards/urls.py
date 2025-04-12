from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from rewards.extensions import CustomTokenObtainPairView, CustomTokenRefreshView, CustomTokenVerifyView


urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path(
        "api/token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"
    ),
    path("api/token/verify/", CustomTokenVerifyView.as_view(), name="token_verify"),
    path("api/", include("rewards.urls")),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


admin.site.site_header = "Панель администрирования и менеджмента контента"
admin.site.index_title = "API-платформа наград пользователям"
