from django.utils import timezone
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from . import core, statistics
from .models import Book, Author, Saga, Edition, BookCopy, Reading
from .forms import ReadingUpdateForm, AddBookForm, SearchBookForm, AddEditionForm


@login_required
def stats(request, year=timezone.now().year):
    """View with statistics for 'year' (default: current year)."""

    state = statistics.State(year, request.user)

    context = {
        "banner": "Stats",
        "books_active": "active",
        "books_stats_active": True,
        "year": year,
        "state": state,
        "current_readings": core.current_readings_by(request.user),
    }

    return render(request, "books/stats.html", context)


@login_required
def index(request):
    """Index view."""

    context = {
        "banner": "Index",
        "books_index_active": True,
        "current_readings": core.current_readings_by(request.user),
        "completed_readings": core.completed_readings_by_year_for(request.user),
    }

    return render(request, "books/index.html", context)


@login_required
def sagas(request):
    """Saga view."""

    saga_list = core.get_saga_data_for(request.user)

    context = {
        "banner": "Sagas",
        "books_sagas_active": True,
        "sagas": saga_list,
    }

    return render(request, "books/sagas.html", context)


@login_required
def book_detail(request, book_id):
    """Detail view for a book."""

    book = Book.objects.get(pk=book_id)
    editions = Edition.objects.filter(book=book)

    context = {
        "banner": book.title,
        "book": book,
        "editions": editions,
    }

    return render(request, "books/book_detail.html", context)


@login_required
def update_reading(request, reading_id):
    """Form to update progress of Reading."""

    reading = Reading.objects.get(pk=reading_id)

    if request.method == "POST":
        form = ReadingUpdateForm(request.POST or None)
        if form.is_valid():
            data = form.cleaned_data
            pages_read = data.get("pages_read")
            percent_read = data.get("percent_read")
            reading.update_progress(pages_read, percent_read)

            return redirect("books:book_detail", book_id=reading.edition.book.id)

    initial = {
        "pages_read": reading.page_progress,
        "percent_read": int(100. * reading.page_progress / reading.edition.pages),
    }
    context = {
        "banner": f"Updating progress for {reading.edition.title}",
        "form": ReadingUpdateForm(initial=initial),
        "reading": reading,
        "book_is_being_read": True,
    }

    return render(request, 'books/update_reading.html', context)


@login_required
def update_book_reading(request, book_id):
    """Update (current) Reading of a given Book."""

    reading = Reading.objects.get(edition__book__pk=book_id, end__isnull=True)

    return redirect("books:update_reading", reading_id=reading.id)


@login_required
def add_book(request):
    """Form to add a new Book."""

    if request.method == "POST":
        form = AddBookForm(request.POST or None)
        if form.is_valid():
            title = form.cleaned_data.get("title")
            if title is not None:
                # Add data:
                book = Book()
                book.title = title
                book.pages = form.cleaned_data.get("pages")
                book.year = form.cleaned_data.get("year")

                # Saga info:
                saga_name = form.cleaned_data.get("saga")
                if saga_name:
                    try:
                        book.saga = Saga.objects.get(name=saga_name)
                    except ObjectDoesNotExist:
                        # Horrible hack to assign to new Saga object the first available id,
                        # because PostgreSQL at Heroku fails to assign an automatic one that
                        # is not duplicated if we simply do saga = Saga(name=saga_name)
                        saga_id = 1
                        for saga_id in range(1, 10000):  # max try 10000 sagas
                            if not Saga.objects.filter(id=saga_id):
                                break
                        saga = Saga(name=saga_name, id=saga_id)
                        saga.save()
                        book.saga = saga
                    book.index_in_saga = form.cleaned_data.get("index")
                book.save()  # we must save BEFORE we add many-to-many field items (author(s) below)

                # Add author data:
                author_names = [a.strip() for a in form.cleaned_data.get("author", "").split(",")]
                for author_name in author_names:
                    try:
                        author = Author.objects.get(name=author_name)
                    except Author.DoesNotExist:
                        author = Author(name=author_name)
                        author.save()
                    book.authors.add(author)

                return redirect("books:book_detail", book_id=book.id)

    initial = {
        "pages": 0,
        "year": 0,
        "saga": None,
        "index": None,
    }
    context = {
        "banner": "Add book",
        "form": AddBookForm(initial=initial),
        "action": "add",
    }

    return render(request, 'books/add_or_modify_book.html', context)


@login_required
def modify_book(request, book_id=None):
    """Form to modify a Book."""

    if request.method == "POST":
        form = AddBookForm(request.POST or None)
        if form.is_valid():
            title = form.cleaned_data.get("title")
            if title is not None:
                book = Book.objects.get(id=book_id)  # book to modify
                book.title = title
                book.year = form.cleaned_data.get("year")

                # Saga info:
                saga_name = form.cleaned_data.get("saga")
                if saga_name:
                    try:
                        book.saga = Saga.objects.get(name=saga_name)
                    except ObjectDoesNotExist:
                        saga_name = Saga(name=saga_name)
                        saga_name.save()
                        book.saga = saga_name
                    book.index_in_saga = form.cleaned_data.get("index")
                book.save()  # we must save BEFORE we add many-to-many field items (author(s) below)

                # Add author data:
                author_names = [a.strip() for a in form.cleaned_data.get("author", "").split(",")]
                for author_name in author_names:
                    try:
                        author = Author.objects.get(name=author_name)
                    except Author.DoesNotExist:
                        author = Author(name=author_name)
                        author.save()
                    book.authors.add(author)

                return redirect("books:book_detail", book_id=book.id)

    book = Book.objects.get(id=book_id)
    initial = {
        "title": book.title,
        "author": ", ".join(book.list_of_authors),
        "year": book.year,
        "saga": book.saga,
        "index": book.index_in_saga,
    }
    form = AddBookForm(initial=initial)

    context = {
        "form": form,
        "book": book,
        "action": "modify",
    }

    return render(request, 'books/add_or_modify_book.html', context)


@login_required
def add_edition(request, book_id=None):
    """Form to create an Edition."""

    book = Book.objects.get(id=book_id)

    if request.method == "POST":
        form = AddEditionForm(request.POST or None)
        if form.is_valid():
            data = form.cleaned_data
            title = data.get("title")
            if title is not None:
                Edition(
                    book=book,
                    title=data["title"],
                    year=data["year"],
                    isbn=data["isbn"],
                    pages=data["pages"],
                ).save()

            return redirect("books:book_detail", book_id=book.id)

    initial = {
        "title": book.title,
        "year": book.year,
        "isbn": None,
        "pages": 0,
    }
    context = {
        "form": AddEditionForm(initial=initial),
        "book": book,
        "action": "add",
    }

    return render(request, 'books/add_or_modify_edition.html', context)


@login_required
def modify_edition(request, edition_id):
    """Form to modify an Edition."""

    edition = Edition.objects.get(id=edition_id)

    if request.method == "POST":
        form = AddEditionForm(request.POST or None)
        if form.is_valid():
            data = form.cleaned_data
            title = data.get("title")
            if title is not None:
                edition.title = data["title"]
                edition.year = data["year"]
                edition.isbn = data["isbn"]
                edition.pages = data["pages"]
                edition.save()

        return redirect("books:book_detail", book_id=edition.book.id)

    initial = {
        "title": edition.title,
        "year": edition.year,
        "isbn": edition.isbn,
        "pages": edition.pages,
    }
    context = {
        "form": AddEditionForm(initial=initial),
        "book": edition.book,
        "action": "modify",
    }

    return render(request, 'books/add_or_modify_edition.html', context)


@login_required
def find_book(request):
    """View to find a Book."""

    if request.method == "POST":
        return handle_find_book_post(request)

    return handle_find_book_get(request)


@login_required
def mark_reading_done(request, reading_id):
    """Come here with a GET to mark a book read (a Reading done)."""

    reading = Reading.objects.get(pk=reading_id)
    reading.mark_read()

    return redirect("books:book_detail", book_id=reading.edition.book.id)


@login_required
def mark_edition_owned(request, edition_id):
    """Come here with a GET to mark a copy of an Edition of a Book as owned."""

    edition = Edition.objects.get(pk=edition_id)
    BookCopy(edition=edition, owner=request.user).save()

    return redirect("books:book_detail", book_id=edition.book.id)


@login_required
def author_detail(request, author_id=None):
    """Detail view for an author."""

    author = Author.objects.get(pk=author_id)

    context = {
        "author": author,
    }

    return render(request, "books/author_detail.html", context)


# Helper functions:
def handle_find_book_post(request):
    form = SearchBookForm(request.POST or None)

    if form.is_valid():
        search_for = form.cleaned_data.get("search_for")
        matching_books = Book.objects.filter(title__icontains=search_for)

        context = {
            "form": SearchBookForm(initial={"search_for": ""}),
            "matching_books": matching_books,
        }

        return render(request, "books/find_book.html", context)

    else:
        return handle_find_book_get(request)


def handle_find_book_get(request):
    context = {
        "banner": "Find book",
        "form": SearchBookForm(initial={"search_for": ""}),
        "matching_books": Book.objects.none(),
    }

    return render(request, "books/find_book.html", context)
