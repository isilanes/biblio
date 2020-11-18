from django.core.management.base import BaseCommand

from apps.books.models import Book, Edition


class Command(BaseCommand):

    help = "Pass from old Book to newer Book + Edition(s)."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **kwargs):
        for book in Book.objects.all():
            edition = Edition()
            edition.book = book
            edition.isbn = "xxx"
            edition.title = book.title
            edition.year = book.year
            edition.pages = book.pages
            edition.save()
            print(edition)
