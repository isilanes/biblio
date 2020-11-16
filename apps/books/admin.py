from django.contrib import admin

from .models import Author, Book, Saga, Reading, ReadingUpdate
from .models import PageUpdateEvent


admin.site.register(Reading)
admin.site.register(ReadingUpdate)


class PageUpdateInline(admin.StackedInline):
    model = PageUpdateEvent
    extra = 0


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    pass


@admin.register(Saga)
class SagaAdmin(admin.ModelAdmin):
    pass


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    fields = ["title", "authors", "pages", "year", "saga", "index_in_saga", "owned", "ordered"]
    list_display = ("title", "year")
    search_fields = ["title"]


@admin.register(PageUpdateEvent)
class PageUpdateEventAdmin(admin.ModelAdmin):
    pass
