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
    deadline = serializers.SerializerMethodField()
    pages_per_day_to_meet_deadline = serializers.SerializerMethodField()

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
            "deadline",
            "pages_per_day_to_meet_deadline",
        )

    @staticmethod
    def get_deadline(obj) -> Optional[str]:
        if obj.deadline is None:
            return None

        ts = obj.deadline.astimezone().strftime("%Y-%m-%d")
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
