from django.utils import timezone
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from . import core, statistics
from .models import Book, Author, Saga, Edition
from .forms import BookForm, AddBookForm, SearchBookForm


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

    context = {
        "banner": "Sagas",
        "books_sagas_active": True,
        "sagas": core.get_saga_data_for(request.user),
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
def update_book_progress(request, book_id):
    """Form to modify state of book."""

    book = Book.objects.get(pk=book_id)

    if request.method == "POST":
        form = BookForm(request.POST or None)
        if form.is_valid():
            pages_read = form.cleaned_data.get("pages_read")
            if pages_read is None and not book.is_currently_being_read_by(request.user):
                book.mark_started_by(request.user)
            elif pages_read > 0:
                book.set_pages_for(request.user, pages_read)

            return redirect("books:book_detail", book_id=book_id)

    initial = {
        "pages_read": book.pages_read_by(request.user),
    }
    form = BookForm(initial=initial)

    context = {
        "banner": f"Modify book: {book.title}",
        "form": form,
        "book": book,
        "book_is_being_read": book.is_currently_being_read_by(request.user),
    }

    return render(request, 'books/update_book_progress.html', context)


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
                book.owned = False

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
    form = AddBookForm(initial=initial)
    context = {
        "banner": "Add book",
        "form": form,
        "action": "add",
    }

    return render(request, 'books/add_or_modify_book.html', context)


def modify_book(request, book_id=None):
    """Form to modify a Book."""

    if request.method == "POST":
        form = AddBookForm(request.POST or None)
        if form.is_valid():
            title = form.cleaned_data.get("title")
            if title is not None:
                book = Book.objects.get(id=book_id)  # book to modify
                book.title = title
                book.pages = form.cleaned_data.get("pages")
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
        "pages": book.pages,
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


def start_book(request):
    """View to start reading a book."""

    if request.method == "POST":
        return handle_start_reading_post(request)

    return handle_start_reading_get(request)


def mark_book_read(request, book_id):
    """Come here with a GET to mark a book read."""

    Book.objects.get(pk=book_id).mark_read()

    return redirect("books:book_detail", book_id=book_id)


def mark_book_owned(request, book_id):
    """Come here with a GET to mark a Book as owned."""

    book = Book.objects.get(pk=book_id)
    book.owned = True
    book.save()

    return redirect("books:book_detail", book_id=book_id)


def author_detail(request, author_id=None):
    """Detail view for an author."""

    author = Author.objects.get(pk=author_id)

    context = {
        "author": author,
    }

    return render(request, "books/author_detail.html", context)


# Helper functions:
def handle_start_reading_post(request):
    form = SearchBookForm(request.POST or None)

    if form.is_valid():
        search_for = form.cleaned_data.get("search_for")
        matching_books = Book.objects.filter(title__icontains=search_for)

        context = {
            "form": SearchBookForm(initial={"search_for": ""}),
            "matching_books": matching_books,
        }

        return render(request, "books/start_book.html", context)

    else:
        return handle_start_reading_get(request)


def handle_start_reading_get(request):
    context = {
        "banner": "Start reading book",
        "form": SearchBookForm(initial={"search_for": ""}),
        "matching_books": Book.objects.none(),
    }

    return render(request, "books/start_book.html", context)
