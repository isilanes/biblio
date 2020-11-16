from django.contrib import admin

from .models import Author, Book, Saga, Reading, ReadingUpdate
from .models import PageUpdateEvent, BookStartEvent


admin.site.register(Reading)
admin.site.register(ReadingUpdate)


class PageUpdateInline(admin.StackedInline):
    model = PageUpdateEvent
    extra = 0


class BookStartInline(admin.StackedInline):
    model = BookStartEvent
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


@admin.register(BookStartEvent)
class BookStartEventAdmin(admin.ModelAdmin):
    pass


@admin.register(PageUpdateEvent)
class PageUpdateEventAdmin(admin.ModelAdmin):
    pass
