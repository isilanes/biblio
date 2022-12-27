from django.contrib import admin
from django.urls import path, include

from . import settings, views


urlpatterns = [
    # Admin view:
    path('admin/', admin.site.urls),

    # User stuff:
    path('user/', views.user, name="user"),

    # Main:
    path('', views.main_index, name="main_index"),
]

# Apps:
for app in settings.EXTRA_APPS:
    app_name = app.split(".")[-1]  # if app = "apps.app_name", "fix" it
    urlpatterns.append(path(f"{app_name}/", include(f"{app}.urls", namespace=app_name)))

# API:
urlpatterns.append(path("api/books/", include("apps.books.api.urls", namespace="api-books")))
