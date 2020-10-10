from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from apps.books.models import BookStartEvent, BookEndEvent, PageUpdateEvent, Reading, ReadingUpdate, Event


class Command(BaseCommand):

    help = "Pass from old PageUpdateEvents to newer Readings."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **kwargs):
        user = User.objects.get(username="isilanes")

        sorted_events = Event.objects.order_by("when").select_subclasses()
        for event in sorted_events:
            if isinstance(event, BookStartEvent):
                reading = Reading(reader=user, book=event.book, start=event.when)
                reading.save()
                try:
                    reading.save()
                except:
                    print("already exists!")
                print(event)
            else:
                print("Unknown", event)
                break

