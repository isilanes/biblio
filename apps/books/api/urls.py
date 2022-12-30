from django.urls import path, include
from rest_framework import routers

from .views import BookViewSet


app_name = "books"

router = routers.DefaultRouter()
router.register(r"books", BookViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
