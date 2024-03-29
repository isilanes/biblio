from django.contrib import admin

from .models import Author, Book, Saga, Reading, ReadingUpdate, Edition, BookCopy


admin.site.register(Author)
admin.site.register(BookCopy)
admin.site.register(Edition)
admin.site.register(Saga)
admin.site.register(Reading)
admin.site.register(ReadingUpdate)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    fields = ["title", "authors", "year", "saga", "index_in_saga", "owned"]
    list_display = ("title", "year")
    search_fields = ["title"]
