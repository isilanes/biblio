from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views

from . import settings, views


urlpatterns = [
    # Admin view:
    path('admin/', admin.site.urls),

    # User stuff:
    path('user/', views.user, name="user"),

    # Main:
    path('', views.main_index, name="main_index"),

    # JWT:
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]

# Apps:
for app in settings.EXTRA_APPS:
    app_name = app.split(".")[-1]  # if app = "apps.app_name", "fix" it
    urlpatterns.append(path(f"{app_name}/", include(f"{app}.urls", namespace=app_name)))

# API:
urlpatterns.append(path("api/", include("apps.books.api.urls", namespace="api-books")))
urlpatterns.append(path("api/", include("apps.readings.api.urls", namespace="api-readings")))
