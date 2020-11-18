from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from apps.books.models import Book, Edition, BookCopy


class Command(BaseCommand):

    help = "Pass from old Book.owned to newer BookCopy (owner + Edition)."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **kwargs):
        user = User.objects.get(username="isilanes")

        for book in Book.objects.filter(owned=True):
            edition = Edition.objects.filter(book=book).first()  # assume 1 edition per book here
            bc = BookCopy(edition=edition, owner=user)
            bc.save()
            print(book)
