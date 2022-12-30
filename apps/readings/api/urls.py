from django.urls import path, include
from rest_framework import routers

from .views import ReadingViewSet, ReadingUpdateViewSet


app_name = "readings"

router = routers.DefaultRouter()
router.register(r"readings", ReadingViewSet, basename="readings")
router.register(r"readingupdates", ReadingUpdateViewSet, basename="readingupdates")

urlpatterns = [
    path("", include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
