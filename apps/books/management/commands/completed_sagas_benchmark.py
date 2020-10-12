from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import OuterRef, Subquery, Case, When, Value, BooleanField

from apps.books.models import Reading, ReadingUpdate, Saga, Book
from biblio.core import TicToc


def start_reading(user, event):
    reading, created = Reading.objects.get_or_create(reader=user, book=event.book, start=event.when)

    if not created:
        raise Exception(f"[EXISTS] {event}")

    print(f"[DONE] {event}")


def end_reading(user, event):
    reading = Reading.objects.get(end=None, reader=user, book=event.book)
    reading.end = event.when
    reading.save()


def page_update(user, event):
    if event.pages_read == 0:
        return

    reading = Reading.objects.get(end=None, reader=user, book=event.book)
    reading_update = ReadingUpdate(reading=reading, page=event.pages_read, date=event.when)
    reading_update.save()
    print(f"[DONE] {event}")


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **kwargs):
        user = User.objects.get(username="isilanes")

        tt = TicToc()
        for saga in Saga.objects.all():
            completed = True
            for book in saga.books:
                if not book.is_already_read_by(user):
                    completed = False
                    break
            if completed:
                print(saga)
        tt.toc("v1")
        print()

        for saga in Saga.objects.all():
            unread = Book.objects.filter(saga=saga).exclude(reading__reader=user, reading__end__isnull=False).exists()
            if not unread:
                print(saga)
        tt.toc("v2")
        print()

        sq = Book.objects\
            .filter(saga=OuterRef("id"))\
            .exclude(reading__reader=user, reading__end__isnull=False)\
            .annotate(is_unread=Case(When(title__isnull=False,  # in other words, always
                                          then=Value(True)), output_field=BooleanField()))[:1]

        sagas = Saga.objects.annotate(has_unreads=Subquery(sq.values('is_unread'))).filter(has_unreads__isnull=True)
        for saga in sagas:
            print(saga)
        tt.toc("v3")
