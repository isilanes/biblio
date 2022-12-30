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


class ReadingSerializer(ReadingBaseSerializer):
    edition = EditionBaseSerializer()

    class Meta:
        model = Reading
        fields = ReadingBaseSerializer.Meta.fields + ("edition",)


class ReadingProgressSerializer(ReadingBaseSerializer):
    title = serializers.StringRelatedField(source="edition.title")
    book_id = serializers.StringRelatedField(source="edition.book.id")
    pages_read = serializers.SerializerMethodField()
    fraction_read = serializers.SerializerMethodField()
    percent_read = serializers.SerializerMethodField()
    pages = serializers.StringRelatedField(source="edition.pages")

    @classmethod
    def setup_eager_loading(cls, queryset, *args, **kwargs):
        latest_ru_subquery = ReadingUpdate.objects.filter(reading=OuterRef('id')).order_by("-date")[:1]

        return queryset.annotate(
            pages_read=Coalesce(Subquery(latest_ru_subquery.values('page')), 0)
        ).annotate(
            fraction_read=as_float(F('pages_read')) / as_float(F('edition__pages'))
        ).annotate(
            percent_read=as_float(F('fraction_read')) * 100.,
        ).order_by("-start")

    class Meta:
        model = Reading
        fields = ReadingBaseSerializer.Meta.fields + (
            "title",
            "edition",
            "book_id",
            "pages_read",
            "fraction_read",
            "percent_read",
            "pages",
        )

    @staticmethod
    def get_pages_read(obj) -> int:
        return getattr(obj, "pages_read", 0)

    @staticmethod
    def get_fraction_read(obj) -> float:
        return getattr(obj, "fraction_read", 0.0)

    @staticmethod
    def get_percent_read(obj) -> float:
        return getattr(obj, "percent_read", 0.0)
