from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from .managers import EventManager


class Author(models.Model):
    name = models.CharField('Name', max_length=200)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.__str__()


class Saga(models.Model):
    name = models.CharField('Name', max_length=300)

    @property
    def books(self):
        """Return sorted list of books in saga."""

        return self.book_set.all().order_by("index_in_saga")

    @property
    def completed(self):
        """True if all books in saga read. False otherwise."""

        for book in self.books:
            if not book.is_already_read:
                return False

        return True

    def completed_by(self, user):
        """True if all books in saga read by user. False otherwise."""

        return not Book.objects.filter(saga=self).exclude(reading__reader=user, reading__end__isnull=False).exists()

    @property
    def owned(self):
        """True if all books in saga owned (read or not). False otherwise."""

        for book in self.books:
            if not book.owned:
                return False

        return True

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.__str__()


class Book(models.Model):
    authors = models.ManyToManyField(Author)
    saga = models.ForeignKey(Saga, blank=True, on_delete=models.CASCADE, default=None, null=True)
    title = models.CharField("Title", max_length=300)
    pages = models.IntegerField("Pages", default=1)
    year = models.IntegerField("Year", default=1)
    index_in_saga = models.IntegerField("Index in saga", default=1)
    owned = models.BooleanField("Owned", default=True)
    ordered = models.BooleanField("Ordered", default=False)

    def mark_read(self):
        """Mark self as read."""

        reading = Reading.objects.get(book=self, end=None)
        reading.end = timezone.now()
        reading.save()

    def mark_started_by(self, user):
        """Mark self as started to read."""

        Reading(book=self, reader=user, start=timezone.now()).save()

    def set_pages_for(self, user=None, pages=None):
        """Mark 'pages' as pages read. Do nothing if 'None'."""

        if pages is not None:
            reading = Reading.objects.get(reader=user, book=self, end=None)
            ReadingUpdate(reading=reading, page=pages, date=timezone.now()).save()

    @property
    def events(self):
        """List of events regarding book, sorted by date."""

        return Event.objects.filter(book=self).order_by("when").select_subclasses()

    def status(self, user):
        """Whether book is not owned, owned but not read, reading, or read."""

        if self.ordered:
            return "ordered"

        if self.is_already_read:
            return "read"

        if self.is_currently_being_read_by(user):
            return "reading"

        if self.owned:
            return "owned"

        return "not-owned"

    def is_currently_being_read_by(self, user):
        """Returns True if it is currently being read. False otherwise."""

        return Reading.objects.filter(book=self, reader=user, end=None).exists()

    @property
    def is_already_read(self):
        """Returns True if it is already read. False otherwise."""

        read = False
        for event in self.events:
            if isinstance(event, BookStartEvent):
                read = False
            elif isinstance(event, BookEndEvent):
                read = True

        return read

    def is_already_read_by(self, user):
        """Returns True if it has already been read by user. False otherwise."""

        return Reading.objects.filter(book=self, reader=user).exclude(end=None).exists()

    def pages_read_by(self, user):
        """How many pages read so far. Only interesting for books currently being read."""

        last_update = ReadingUpdate.objects\
            .filter(reading__book=self, reading__end=None)\
            .order_by("date").last()

        if last_update is None:
            return 0
        else:
            return last_update.page

    def percent_read_by(self, user):

        return 100. * self.pages_read_by(user) / self.pages

    @property
    def date_read(self):
        """Return date of most recent time we finished reading it. None if never."""

        try:
            return BookEndEvent.objects.filter(book=self).order_by("-when")[0].when
        except IndexError:
            return None

    @property
    def list_of_authors(self):
        """Return Authors as a list of strings."""

        return [a.name for a in self.authors.all()]

    def __str__(self):
        return self.title


class Event(models.Model):
    user = models.ForeignKey(User, blank=False, on_delete=models.CASCADE, default=1)
    book = models.ForeignKey(Book, blank=True, on_delete=models.CASCADE)
    when = models.DateTimeField("When", blank=True, default=timezone.now)
    objects = EventManager()


class PageUpdateEvent(Event):
    """The event of updating the pages of a book I have already read."""

    pages_read = models.IntegerField("Pages read", default=0)

    @property
    def page_equivalent(self):
        return self.pages_read

    @property
    def progress_percent(self):
        return 100. * self.pages_read / self.book.pages

    def __str__(self):
        return f"{self.pages_read} pages read on '{self.book}'"

    def __unicode__(self):
        return self.__str__()


class BookStartEvent(Event):
    """The event of starting reading a book."""

    page_equivalent = 0
    progress_percent = 0

    def __str__(self):
        return f"'{self.book}' started"

    def __unicode__(self):
        return self.__str__()


class BookEndEvent(Event):
    """The event of finishing reading a book."""

    progress_percent = 100

    @property
    def page_equivalent(self):
        return self.book.pages

    def __str__(self):
        return f"'{self.book}' finished"

    def __unicode__(self):
        return self.__str__()


class Reading(models.Model):
    reader = models.ForeignKey(User, blank=False, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, blank=True, on_delete=models.CASCADE)
    start = models.DateTimeField("Start", blank=False, default=timezone.now)
    end = models.DateTimeField("End", blank=True, default=None, null=True)

    def __str__(self):
        if self.end is None:
            return f"'{self.book}' started on {self.start} by {self.reader}"
        else:
            return f"'{self.book}' ended on {self.end} by {self.reader}"


class ReadingUpdate(models.Model):
    reading = models.ForeignKey(Reading, blank=False, on_delete=models.CASCADE)
    page = models.IntegerField("Page", default=0)
    date = models.DateTimeField("Date", blank=True, default=timezone.now)

    def __str__(self):
        return f"{self.page} pages on {self.reading} at {self.date}"
