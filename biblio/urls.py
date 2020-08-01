from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import settings, views
from apps.login import views as login_views

EXCLUDED_EXTRA_APPS = ["login"]  # do not add this to urlpatterns

urlpatterns = [
    # Admin view:
    path('admin/', admin.site.urls),

    # User stuff:
    path('user/', views.user, name="user"),

    #path('login/', auth_views.LoginView.as_view(template_name="login/login.html"), name='login'),
    #path('logout/', login_views.logout, name='logout'),
    #path('signup/', login_views.signup, name='signup'),

    # Main:
    path('', views.main_index, name="main_index"),
]

# Apps:
for app in settings.EXTRA_APPS:
    app_name = app.split(".")[-1]  # if app = "apps.app_name", "fix" it
    urlpatterns.append(path(f'{app_name}/', include(f'{app}.urls', namespace=app_name)))
