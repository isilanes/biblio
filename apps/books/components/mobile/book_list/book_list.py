from django_components import Component, register

from apps.books.models import Book


@register("book_list")
class BookList(Component):
    template_file = "book_list.html"
    css_file = "book_list.css"
    js_file = "book_list.js"

    def get_context_data(self, title: str, books: list[Book]):
        return {
            "title": title,
            "books": books,
        }
