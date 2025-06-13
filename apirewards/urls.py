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
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
"""
Вот здесь была ошибка.
В приложении не работал редирект с адресов без висячих слэшей, несмотря
на наличие `APPEND_SLASH = True` в `settings.py`. То есть, запрос по адресу
`http://localhost:8000/swagger` получал от приложения 404 ответ, хотя есть
адрес `http://localhost:8000/swagger/`. Да, это разные адреса, но APPEND_SLASH
в настройках должен сначала проверить `swagger` в списке доступных маршрутов,
а затем, если не нашел, поискать `swagger/`. А тут почему-то не работает.

Если присмотреться к тексту страницы 404 ошибки в дебаг-режиме, то стоит
обратить внимание на следующее:

```python
Page not found (404)
“/app/swagger” не существует
Request Method:	GET
Request URL:	http://localhost:8080/api/token
Raised by:	django.views.static.serve
Using the URLconf defined in apirewards.urls, Django tried these URL patterns, in this order:

admin/
...
^static/(?P<path>.*)$
^(?P<path>.*)$
The current path, api/token, matched the last one.
```

Буквально последняя строка означает: адрес, который ты запрашиваешь, то есть
`http://localhost:8000/swagger` попал в последний шаблон-регулярку,
`^(?P<path>.*)$`, под который, как видно, попадают ВООБЩЕ ВСЕ маршруты, если
они не застряли на маршрутах выше по списку.
Если посмотреть повыше, видно, что приложение пытается искать файл “/app/swagger”,
который, конечно же, не существует. Ну или существует, если он у вас зачем-то
есть в проекте.

Я долго ломал голову, почему так, ковырял всю последовательность инструкций,
которая так или иначе работает со статикой в Джанго и т.д.

Оказалось, что все гораздо проще.
Я почти все правильно сделал:
1) в settings.py написал вот так:
```python
STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / 'static'
```
2) в urls.py написал вот так:
```python
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```
3) перед запуском приложения (использую uWSGI) выполнил
```bash
./manage.py collectstatic
```

И вот так все работает. Но я зачем-то на всякий случай в urls.py написал так:
```python
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

Ну типа "пускай стандартная функция static" работает еще и с медиа.
Но функция-то требует передачи ей путей, где будут лежать медиафайлы.
А их-то нет в `settings.py`. Ну не задавал их там никто, потому что в проекте
не предполагается наличие медиафайлов в каком бы то ни было виде.

В случае со статикой это было бы проблемой - фреймворк просто выдаст при запуске
ошибку
```shell
django.core.exceptions.ImproperlyConfigured: Empty static prefix not permitted
```
А вот с медиафайлами такие приколы прокатывают! И если в `settings.py` нет
```python
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```
фреймворк использует стандартные значения:
```python
>>> from django.conf import settings
>>> settings.MEDIA_ROOT
''
>>> settings.MEDIA_URL
'/'
```

Таким образом, когда отрабатывается запрос на `http://localhost:8000/swagger`:
1) `swagger` не находится в списке доступных путей;
2) поиск доходит до регулярки `^(?P<path>.*)$`, которая принимает ЛЮБУЮ
строку, которая находится в пути,
3) а затем пытается найти в корневой директории проекта (потому что 
`MEDIA_URL == "/"`, то есть корневая папка проекта - `BASE_DIR`) файл с именем
`swagger` - ну или любой другой. Ровно так, как это работает с выдачей сервером
медиафайлов.

А такого файла нет. Вот и получается 404 ошибка.
И `APPEND_SLASH` не срабатывает, потому что он начинает работать только ПОСЛЕ
того, как пробежится полностью по списку известных путей, и, если не найдет
соответствия, уже добавит в конец искомого пути "/", после чего поищет еще раз.
А здесь поиск прерывается последней регуляркой, которая стоит в самом конце.

Фреймворк оказался умнее человека - никогда такого не было и вот опять.

"""

admin.site.site_header = "Панель администрирования и менеджмента контента"
admin.site.index_title = "API-платформа наград пользователям"
