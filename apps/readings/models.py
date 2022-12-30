from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Reading(models.Model):
    reader = models.ForeignKey(User, blank=False, on_delete=models.CASCADE)
    edition = models.ForeignKey(
        "books.Edition",
        blank=True,
        on_delete=models.CASCADE,
        default=1,
    )
    start = models.DateTimeField("Start", blank=False, default=timezone.now)
    end = models.DateTimeField("End", blank=True, default=None, null=True)

    objects = models.Manager()

    class Meta:
        db_table = "books_reading"

    @property
    def page_progress(self):
        latest_update = ReadingUpdate.objects.filter(reading=self).order_by("date").last()

        return getattr(latest_update, "page", 0)

    def mark_read(self):
        self.end = timezone.now()
        self.save()

    def __str__(self):
        if self.end is None:
            return f"'{self.edition}' started on {self.start} by {self.reader}"
        else:
            return f"'{self.edition}' ended on {self.end} by {self.reader}"


class ReadingUpdate(models.Model):
    reading = models.ForeignKey(Reading, blank=False, on_delete=models.CASCADE)
    page = models.IntegerField("Page", default=0)
    date = models.DateTimeField("Date", blank=True, default=timezone.now)

    objects = models.Manager()

    class Meta:
        db_table = "books_readingupdate"

    def __str__(self):
        return f"{self.page} pages on {self.reading} at {self.date}"
