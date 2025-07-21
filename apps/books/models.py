from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from apps.readings.lib.custom_definitions import ReadingStatus
from apps.readings.models import Reading, ReadingUpdate


class Author(models.Model):
    name = models.CharField('Name', max_length=200)

    objects = models.Manager()

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.__str__()


class Saga(models.Model):
    name = models.CharField('Name', max_length=300)

    objects = models.Manager()

    @property
    def books(self):
        """Return sorted list of books in saga."""

        return self.book_set.all().order_by("index_in_saga")

    def completed_by(self, user):
        """True if all books in saga read by user. False otherwise."""

        return not Book.objects.filter(saga=self).exclude(reading__reader=user, reading__end__isnull=False).exists()

    def owned_by(self, user):
        """TODO
        True if all books in saga owned (read or not) by user. False otherwise."""

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
    year = models.IntegerField("Year", default=1)
    index_in_saga = models.IntegerField("Index in saga", default=1)
    owned = models.BooleanField("Owned", default=True)

    objects = models.Manager()

    def mark_started_by(self, user):
        """Mark self as started to read."""

        Reading(book=self, reader=user, start=timezone.now()).save()

    def set_pages_for(self, user=None, pages=None):
        """Mark 'pages' as pages read. Do nothing if 'None'."""

        if pages is not None:
            reading = Reading.objects.get(reader=user, book=self, end=None)
            ReadingUpdate(reading=reading, page=pages, date=timezone.now()).save()

    def status(self, user):
        """Whether book is not owned, owned but not read, reading, or read."""

        if self.is_already_read_by(user):
            return "read"

        if self.is_currently_being_read_by(user):
            return "reading"

        if self.owned:
            return "owned"

        return "not-owned"

    def is_currently_being_read_by(self, user):
        """Returns True if it is currently being read. False otherwise."""

        return Reading.objects.filter(edition__book=self, reader=user, end=None).exists()

    def is_already_read_by(self, user):
        """Returns True if it has already been read by user. False otherwise."""

        return Reading.objects.filter(edition__book=self, reader=user, status=ReadingStatus.COMPLETED).exists()

    def is_owned_by(self, user):
        return BookCopy.objects.filter(edition__book=self, owner=user).exists()

    def pages_read_by(self, user):
        """How many pages read so far. Only interesting for books currently being read."""

        last_update = self._last_update

        if last_update is None:
            return 0
        else:
            return last_update.page

    def percent_read_by(self, user):

        return 100. * self.pages_read_by(user) / self._last_update_of(user).edition.pages

    def _last_update_of(self, user):
        return ReadingUpdate.objects.filter(
            reading__book=self,
            reading__end=None,
            reader=user,
        ).order_by("date").last()

    @property
    def list_of_authors(self):
        """Return Authors as a list of strings."""

        return [a.name for a in self.authors.all()]

    def __str__(self):
        return self.title

    def __lt__(self, other):
        return self.title < other.title


class Edition(models.Model):
    book = models.ForeignKey(Book, blank=True, on_delete=models.CASCADE)
    isbn = models.CharField("ISBN", max_length=16)
    title = models.CharField("Title", max_length=300)
    year = models.IntegerField("Year", default=1)
    pages = models.IntegerField("Pages", default=1)

    objects = models.Manager()

    @property
    def owned(self):
        return BookCopy.objects.filter(edition=self).exists()

    def __str__(self):
        return f"{self.year} edition of '{self.book}' ({self.isbn})"


class BookCopy(models.Model):
    """A copy of a Book, i.e. an Edition+Owner combination."""
    edition = models.ForeignKey(Edition, blank=True, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, blank=True, on_delete=models.CASCADE)

    objects = models.Manager()

    def __str__(self):
        return f"Copy of {self.edition}, owned by {self.owner}"
