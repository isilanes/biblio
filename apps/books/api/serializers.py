from rest_framework.serializers import ModelSerializer

from apps.books.models import Book, Edition


class BookDetailSerializer(ModelSerializer):

    class Meta:
        model = Book
        fields = ("title", "year")


class EditionBaseSerializer(ModelSerializer):

    class Meta:
        model = Edition
        fields = ("id", "isbn")


class EditionSerializer(EditionBaseSerializer):

    class Meta:
        fields = EditionBaseSerializer.Meta.fields + ("title",)
