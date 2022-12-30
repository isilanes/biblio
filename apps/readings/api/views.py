from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.readings.models import Reading
from apps.readings.api.serializers import ReadingSerializer, ReadingProgressSerializer


class ReadingViewSet(ModelViewSet):
    serializer_class = ReadingSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user

        return Reading.objects.filter(reader=user)

    @action(detail=False, methods=['get'], url_path="progress")
    def progress(self, request=None):
        qs = self.get_queryset()
        qs = qs.filter(end__isnull=True)
        qs = ReadingProgressSerializer.setup_eager_loading(qs)

        data = ReadingProgressSerializer(qs, many=True).data

        return Response(data=data)

