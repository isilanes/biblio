from django.urls import path
from django.contrib.auth import views as auth_views

from . import views


app_name = "login"


urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name="login/login.html"), name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
]
