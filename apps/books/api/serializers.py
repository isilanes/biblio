from rest_framework.serializers import HyperlinkedModelSerializer

from apps.books.models import Book


class BookDetailSerializer(HyperlinkedModelSerializer):

    class Meta:
        model = Book
        fields = ("title", "year")
