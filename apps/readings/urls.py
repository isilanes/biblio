from django.urls import path

from . import views


app_name = "readings"


urlpatterns = [
    path("set_deadline/<int:reading_id>", views.set_deadline, name="set_deadline"),
]
