from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from apps.books.models import Book
from apps.books.api.serializers import BookDetailSerializer


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookDetailSerializer
    permission_classes = (permissions.IsAuthenticated,)

