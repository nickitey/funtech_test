from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView


"""
Практический смысл этих классов только один. В условиях тестового задания было
предоставление рабочего интерфейса для API на базе Swagger UI.
В API используется django app simplejwt, который содержит готовые CBV для работы
с токенами.
Для автогенерации Swagger UI используется django app drf-spectacular.
В процессе автогенерации интерактивной документации модули данной библиотеки
используют префиксы путей эндпоинтов в качестве тегов для группировки эндпоинтов.
По условиям тестового задания, обращение ко всем эндпоинтам доступно по пути
api/*. Соответственно, в документации все доступные эндпоинты сгруппированы
вместе в категорию "api".
Если с пользовательскими views сложности в присвоении им тегов не возникает,
то views сторонних библиотек недоступны.
Соответственно, рабочим решением является использование собственных views,
которые одновременно имеют за счет наследования весь функционал стандартных
views библиотеки simplejwt, но при этом еще явно отнесены к одной категории
эндпоинтов в документации.
"""

@extend_schema(tags=['Токены'])
class CustomTokenObtainPairView(TokenObtainPairView):
    pass

@extend_schema(tags=['Токены'])
class CustomTokenRefreshView(TokenRefreshView):
    pass

@extend_schema(tags=['Токены'])
class CustomTokenVerifyView(TokenVerifyView):
    pass
