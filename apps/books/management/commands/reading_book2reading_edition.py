from django.core.management.base import BaseCommand

from apps.books.models import Edition, Reading


class Command(BaseCommand):

    help = "Pass from old Book to newer Book + Edition(s)."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **kwargs):
        for reading in Reading.objects.all():
            book = reading.book
            edition = Edition.objects.filter(book=book).first()
            reading.edition = edition
            reading.save()
            print(reading, edition)
