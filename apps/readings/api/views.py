from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.readings.lib.controllers import update_reading_progress
from apps.readings.models import Reading, ReadingUpdate
from apps.readings.api.serializers import (
    ReadingSerializer,
    ReadingProgressSerializer,
    ReadingBaseSerializer,
    ReadingUpdateSerializer,
    ReadingUpdateBaseSerializer,
)


class ReadingViewSet(ModelViewSet):
    serializer_class = ReadingSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user

        qs = Reading.objects.filter(reader=user)
        qs = ReadingBaseSerializer.setup_eager_loading(qs)

        return qs

    @action(detail=False, methods=['get'], url_path="progress")
    def progress(self, request=None):
        qs = self.get_queryset()
        qs = qs.filter(end__isnull=True)

        data = ReadingProgressSerializer(qs, many=True).data

        return Response(data=data)


class ReadingUpdateViewSet(ModelViewSet):
    serializer_class = ReadingUpdateSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user

        qs = ReadingUpdate.objects.filter(reading__reader=user).order_by("date")
        qs = ReadingUpdateBaseSerializer.setup_eager_loading(qs)

        return qs

    def create(self, request, *args):

        reading_id = request.data.get("reading")
        pages = request.data.get("pages")
        percent = request.data.get("percent")

        qs = Reading.objects.filter(id=reading_id)

        data = {}
        if qs:
            reading = qs.first()
            update_reading_progress(reading, pages, percent)
            qs = ReadingBaseSerializer.setup_eager_loading(qs)
            reading = qs.first()
            data = ReadingProgressSerializer(reading).data

        return Response(data)
