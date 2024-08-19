from typing import Optional

from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.readings.lib.controllers import update_reading_progress
from apps.readings.lib.custom_definitions import ReadingStatus
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

    @action(detail=False, methods=['GET'], url_path="progress")
    def progress(self, request=None):
        """
        Return Readings that are ongoing, and what progress it has been made on them.
        """
        qs = self.get_queryset()
        qs = qs.filter(status=ReadingStatus.STARTED)

        data = ReadingProgressSerializer(qs, many=True).data

        return Response(data=data)

    @action(detail=True, methods=['POST'], url_path="set_deadline_drf")
    def set_deadline(self, request=None, pk: Optional[int] = None):
        """
        Set a deadline on a Reading.
        """
        qs = self.get_queryset()
        reading = qs.filter(id=pk).first()

        if not reading:
            return {}

        return Response(data={1: 2})


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
