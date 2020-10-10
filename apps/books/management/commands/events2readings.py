from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from apps.books.models import BookStartEvent, BookEndEvent, PageUpdateEvent, Reading, ReadingUpdate, Event


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

    help = "Pass from old PageUpdateEvents to newer Readings."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **kwargs):
        user = User.objects.get(username="isilanes")
        ReadingUpdate.objects.all().delete()
        Reading.objects.all().delete()

        sorted_events = Event.objects.order_by("when").select_subclasses()
        for event in sorted_events:
            if isinstance(event, BookStartEvent):
                start_reading(user, event)
            elif isinstance(event, BookEndEvent):
                end_reading(user, event)
            elif isinstance(event, PageUpdateEvent):
                page_update(user, event)
            else:
                print(f"[UNKNOWN] {event} of type {type(event)}")
                break

