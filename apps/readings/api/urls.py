from django.urls import path, include
from rest_framework import routers

from .views import ReadingViewSet


app_name = "readings"

router = routers.DefaultRouter()
router.register(r"", ReadingViewSet, basename="readings")

urlpatterns = [
    path("", include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
