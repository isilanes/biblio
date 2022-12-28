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
        if latest_update is None:
            return 0
        else:
            return latest_update.page

    def update_progress(self, pages=None, percent=None):
        max_pages = self.edition.pages
        new_pages = 0

        if percent is not None and percent <= 100:
            new_pages = int(percent * max_pages / 100)

        new_pages = max(pages, new_pages)

        if self.page_progress < new_pages <= max_pages:  # only save if an update
            ReadingUpdate(reading=self, page=new_pages, date=timezone.now()).save()

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
