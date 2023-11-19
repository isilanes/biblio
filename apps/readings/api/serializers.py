from datetime import timedelta
from typing import Optional

from django.db.models import Subquery, F, OuterRef
from django.db.models.functions import Coalesce
from django.utils import timezone
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
        latest_ru_subquery = ReadingUpdate.objects.filter(reading=OuterRef('id')).order_by("-date")[:1]

        return queryset.annotate(
            pages_read=Coalesce(Subquery(latest_ru_subquery.values('page')), 0)
        ).annotate(
            fraction_read=as_float(F('pages_read')) / as_float(F('edition__pages'))
        ).annotate(
            percent_read=as_float(F('fraction_read')) * 100.,
        ).order_by("-start")

    @staticmethod
    def get_pages_read(obj) -> int:
        return getattr(obj, "pages_read", 0)

    @staticmethod
    def get_fraction_read(obj) -> float:
        return getattr(obj, "fraction_read", 0.0)

    @staticmethod
    def get_percent_read(obj) -> float:
        return getattr(obj, "percent_read", 0.0)


class ReadingSerializer(ReadingBaseSerializer):
    title = serializers.CharField(source="edition.title")
    pages_read = serializers.SerializerMethodField()
    edition = EditionBaseSerializer()

    class Meta:
        model = Reading
        fields = ReadingBaseSerializer.Meta.fields + (
            "title",
            "edition",
            "pages_read",
        )


class ReadingProgressSerializer(ReadingBaseSerializer):
    title = serializers.CharField(source="edition.title")
    book_id = serializers.IntegerField(source="edition.book.id")
    pages_read = serializers.SerializerMethodField()
    fraction_read = serializers.SerializerMethodField()
    percent_read = serializers.SerializerMethodField()
    pages = serializers.IntegerField(source="edition.pages")
    isbn = serializers.CharField(source="edition.isbn")
    deadline = serializers.SerializerMethodField()
    pages_per_day_to_meet_deadline = serializers.SerializerMethodField()

    class Meta:
        model = Reading
        fields = ReadingBaseSerializer.Meta.fields + (
            "title",
            "isbn",
            "book_id",
            "pages",
            "pages_read",
            "fraction_read",
            "percent_read",
            "deadline",
            "pages_per_day_to_meet_deadline",
        )

    @staticmethod
    def get_deadline(obj) -> Optional[str]:
        if obj.deadline is None:
            return None

        ts = obj.deadline.astimezone().strftime("%Y-%m-%d %H:%M")
        if obj.deadline_percent == 100:
            return ts

        return f"{ts} ({obj.deadline_percent}%)"

    @staticmethod
    def get_pages_per_day_to_meet_deadline(obj) -> Optional[float]:
        """
        Given the current progress in the Reading and the deadline date (and percent), if any,
        calculate the amount of pages per day one would have to read to meet the deadline.
        """
        if obj.deadline is None:
            return None

        dt = obj.deadline - timezone.now()

        if dt < timedelta(seconds=0):
            return None

        dp = obj.deadline_percent*obj.edition.pages/100 - obj.page_progress

        if dp <= 0:
            return None

        return 86400*dp/dt.total_seconds()


class ReadingUpdateBaseSerializer(ModelSerializer):
    class Meta:
        model = ReadingUpdate
        fields = ("id",)

    @classmethod
    def setup_eager_loading(cls, queryset, *args, **kwargs):
        return queryset


class ReadingUpdateSerializer(ReadingUpdateBaseSerializer):
    pass
