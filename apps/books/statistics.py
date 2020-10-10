from datetime import datetime

from django.db.models import Sum, Subquery, OuterRef, F

from . import core
from biblio.models import UserPreferences
from .models import Reading, ReadingUpdate


class State(object):
    """Encapsulate all State stuff."""

    def __init__(self, year, user):
        self.year = year
        self.user = user
        try:
            self.goal = UserPreferences.objects.get(user=user).books_per_year
        except UserPreferences.DoesNotExist:
            self.goal = 1

        # Helpers for properties:
        self._books_read = None
        self._pages_read = None

    @property
    def pages_per_book(self):
        try:
            return self.pages_read / self.books_read
        except ZeroDivisionError:
            return 0

    @property
    def pages_read(self):
        """How many pages read this year."""

        if not self._pages_read:
            self._books_read, self._pages_read = self._books_and_pages_so_far()

        return self._pages_read

    @property
    def books_read(self):
        """How many books read this year."""

        if not self._books_read:
            self._books_read, self._pages_read = self._books_and_pages_so_far()

        return self._books_read

    @property
    def expected_books_so_far(self):
        """How many books we should have read so far in the year."""

        return self.goal * self.year_fraction_passed

    @property
    def expected_books_by_end_of_year(self):
        """How many books we will have read by the end of the year, at current rate."""

        return self.books_read / self.year_fraction_passed

    @property
    def book_superavit(self):
        """How many books ahead we are in the book count up to now in the year."""

        return self.books_read - self.expected_books_so_far

    @property
    def book_superavit_percent(self):
        """How many books ahead we are in the book count up to now in the year,
        as a percent of total books to read."""

        return 100. * self.book_superavit / self.goal

    @property
    def book_percent_read(self):
        """Percentage of books read, out of total books to read."""

        return 100. * self.books_read / self.goal

    @property
    def book_deficit_percent(self):
        return -1. * self.book_superavit_percent

    @property
    def pages_per_day(self):
        return self.pages_read / self.days_so_far

    @property
    def books_per_week(self):
        return 7 * self.books_per_day

    @property
    def books_per_day(self):
        return self.books_read / self.days_so_far

    @property
    def required_books(self):
        """How many books left to read this year."""

        return self.goal - self.books_read

    @property
    def required_pages_per_day(self):
        """How many pages we have to read, per day, for the rest of the year."""

        return self.pages_per_book * self.required_books_per_day

    @property
    def required_books_per_week(self):
        """Books/week we need to read for the remainder of the year."""

        return 7 * self.required_books_per_day

    @property
    def required_books_per_day(self):
        """Books/day we need to read for the remainder of the year."""

        return self.required_books / self.remaining_days

    @property
    def remaining_days(self):
        return 365 - self.days_so_far

    @property
    def year_fraction_passed(self):
        """Fraction of year already passed. 1.0 if not current year."""

        now = datetime.now()

        if self.year == now.year:
            passed_seconds = (now - datetime(self.year, 1, 1)).total_seconds()

            return passed_seconds / 31536000.  # 31536000 seconds in a year

        else:
            return 1.0

    @property
    def days_so_far(self):
        """Days so far in this year. 365 if not current year."""

        return self.year_fraction_passed * 365

    def _books_and_pages_so_far(self):
        """Number of books and pages read during year."""

        # Stats from finished books:
        finished_readings_qs = Reading.objects.filter(end__year=self.year, reader=self.user)

        books_this_year = finished_readings_qs.count()
        pages_this_year = finished_readings_qs.aggregate(total_pages=Sum('book__pages')).get('total_pages', 0)

        # Stats from books currently being read:
        latest_ru_subquery = ReadingUpdate.objects.filter(reading=OuterRef('id')).order_by("-date")[:1]

        started_readings_qs = Reading.objects.filter(start__year=self.year, end=None, reader=self.user)\
            .annotate(pages=Subquery(latest_ru_subquery.values('page')))\
            .annotate(fraction=core.as_float(F('pages')) / core.as_float(F('book__pages')))

        data = started_readings_qs.aggregate(total_pages=Sum('pages'), total_fraction=Sum('fraction'))
        books_this_year += data["total_fraction"]
        pages_this_year += data["total_pages"]

        return books_this_year, pages_this_year


