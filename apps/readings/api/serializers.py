from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from apps.books.api.serializers import EditionBaseSerializer
from apps.readings.models import Reading


class ReadingBaseSerializer(ModelSerializer):

    class Meta:
        model = Reading
        fields = ("id",)


class ReadingSerializer(ReadingBaseSerializer):
    edition = EditionBaseSerializer()

    class Meta:
        model = Reading
        fields = ReadingBaseSerializer.Meta.fields + ("edition",)


class ReadingProgressSerializer(ReadingBaseSerializer):

    class Meta:
        model = Reading
        fields = ReadingBaseSerializer.Meta.fields + ("edition",)
