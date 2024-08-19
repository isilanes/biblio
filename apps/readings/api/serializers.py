from django.db.models import Subquery, F, OuterRef
from django.db.models.functions import Coalesce
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from apps.books.api.serializers import EditionBaseSerializer
from apps.readings.models import Reading, ReadingUpdate
from biblio.core import as_float


class ReadingBaseSerializer(ModelSerializer):

    class Meta:
        model = Reading
        fields = ("id",)

    @classmethod
    def setup_eager_loading(cls, queryset, *args, **kwargs):
        return queryset.order_by("-start")

    @staticmethod
    def get_fraction_read(obj) -> float:
        current = getattr(obj, "current_page", 0.0)
        total = getattr(obj.edition, "pages", 1)

        return current / total

    @staticmethod
    def get_percent_read(obj) -> float:
        current = getattr(obj, "current_page", 0.0)
        total = getattr(obj.edition, "pages", 1)

        return 100 * current / total


class ReadingSerializer(ReadingBaseSerializer):
    title = serializers.CharField(source="edition.title")
    edition = EditionBaseSerializer()

    class Meta:
        model = Reading
        fields = ReadingBaseSerializer.Meta.fields + (
            "title",
            "edition",
            "current_page",
        )


class ReadingProgressSerializer(ReadingBaseSerializer):
    title = serializers.CharField(source="edition.title")
    book_id = serializers.IntegerField(source="edition.book.id")
    fraction_read = serializers.SerializerMethodField()
    percent_read = serializers.SerializerMethodField()
    pages = serializers.IntegerField(source="edition.pages")
    isbn = serializers.CharField(source="edition.isbn")

    class Meta:
        model = Reading
        fields = ReadingBaseSerializer.Meta.fields + (
            "title",
            "isbn",
            "book_id",
            "pages",
            "current_page",
            "fraction_read",
            "percent_read",
        )


class ReadingUpdateBaseSerializer(ModelSerializer):
    class Meta:
        model = ReadingUpdate
        fields = ("id",)

    @classmethod
    def setup_eager_loading(cls, queryset, *args, **kwargs):
        return queryset


class ReadingUpdateSerializer(ReadingUpdateBaseSerializer):
    pass
