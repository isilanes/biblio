from django.contrib import admin

from .models import Author, Book, Saga, Reading, ReadingUpdate


admin.site.register(Reading)
admin.site.register(ReadingUpdate)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    pass


@admin.register(Saga)
class SagaAdmin(admin.ModelAdmin):
    pass


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    fields = ["title", "authors", "pages", "year", "saga", "index_in_saga", "owned"]
    list_display = ("title", "year")
    search_fields = ["title"]
