from typing import Optional

from django.utils import timezone
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from . import core, statistics
from .models import Book, Author, Saga, Edition, BookCopy
from .forms import ReadingUpdateForm, AddBookForm, AddEditionForm, SearchAuthorOrBookForm
from apps.readings.api.views import ReadingViewSet
from apps.readings.lib.controllers import update_reading_progress
from apps.readings.models import Reading


@login_required
def stats(request, year: Optional[int] = None):
    """View with statistics for 'year' (default: current year)."""

    year = year or timezone.now().year

    state = statistics.State(year, request.user)
    progress_response = ReadingViewSet(request=request).progress()

    context = {
        "banner": None,
        "books_active": "active",
        "books_stats_active": True,
        "year": year,
        "state": state,
        "current_readings": progress_response.data,
    }

    return render(request, "books/stats.html", context)


@login_required
def reading_and_read(request):
    """Index view."""

    context = {
        "banner": None,
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
def bibliography(request, author_id: int):
    """Bibliography of an author."""

    author = Author.objects.filter(id=author_id).first()
    books = Book.objects.filter(authors=author)

    author_sagas = {}
    for book in books:
        if book.saga not in author_sagas:
            author_sagas[book.saga] = []
        author_sagas[book.saga].append(book)

    bg = {}
    for saga, books in author_sagas.items():
        dsu = sorted([(b.index_in_saga, b) for b in books])
        key = saga or "No saga"
        bg[key] = [b for _, b in dsu]

    context = {
        "bibliography": bg,
    }

    return render(request, "books/bibliography.html", context)


@login_required
def book_detail(request, book_id):
    """Detail view for a book."""

    book = Book.objects.get(pk=book_id)
    editions = Edition.objects.filter(book=book)

    context = {
        "banner": book.title,
        "book": book,
        "editions": editions,
        "is_being_read": book.is_currently_being_read_by(request.user),
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
            update_reading_progress(reading, pages_read, percent_read)

            return redirect("books:stats")

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

    reading = Reading.objects.get(
        edition__book__pk=book_id,
        reader=request.user,
        end__isnull=True,
    )

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
        "add_book_active": True,
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
                    except Author.DoesNotExist:  # noqa
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
        "banner": f"Edition of '{book}'",
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
        "banner": f"Edition of '{edition.book}'",
        "form": AddEditionForm(initial=initial),
        "book": edition.book,
        "action": "modify",
    }

    return render(request, 'books/add_or_modify_edition.html', context)


@login_required
def find_book(request):
    """View to find a Book."""

    # Default for GET:
    matching_books = Book.objects.none()
    matching_authors = Author.objects.none()
    form = SearchAuthorOrBookForm(initial={"query": "", "search_type": "book"})

    if request.method == "POST":
        posted_form = SearchAuthorOrBookForm(request.POST or None)

        if posted_form.is_valid():
            search_for = posted_form.cleaned_data.get("query")
            search_type = posted_form.cleaned_data.get("search_type")
            if search_type == "book":
                matching_books = Book.objects.filter(title__icontains=search_for)
            else:
                matching_authors = Author.objects.filter(name__icontains=search_for)
            form = posted_form

    context = {
        "banner": None,
        "find_book_active": True,
        "form": form,
        "matching_books": matching_books,
        "matching_authors": matching_authors,
    }

    return render(request, "books/find_book.html", context)


@login_required
def mark_reading_done(request, reading_id):
    """
    # TODO: deprecate?
    Come here with a GET to mark a book read (a Reading done).
    """
    reading = Reading.objects.get(pk=reading_id)
    reading.mark_read()

    return redirect("books:book_detail", book_id=reading.edition.book.id)


@login_required
def mark_reading_dnf(request, reading_id):
    """
    # TODO: deprecate?
    Come here with a GET to mark a book did not finish (a Reading DNF).
    """
    reading = Reading.objects.get(pk=reading_id)
    reading.mark_dnf()

    return redirect("books:book_detail", book_id=reading.edition.book.id)


@csrf_exempt
@login_required
def mark_reading_pages(request, reading_id):
    """Come here with a POST to mark 'pages' pages read on a book."""

    reading = Reading.objects.get(pk=reading_id)
    new_pages = request.POST.get("new_pages")

    if new_pages is not None:
        update_reading_progress(reading=reading, pages=int(new_pages))

    return JsonResponse({})


@csrf_exempt
@login_required
def mark_reading_finished(request, reading_id):
    """Come here with a POST to mark a book as read."""

    reading = Reading.objects.get(pk=reading_id)
    reading.mark_read()

    return JsonResponse({})


@csrf_exempt
@login_required
def mark_reading_dnf_rest(request, reading_id):
    """
    TODO: use ReadingViewSet
    Come here with a POST to mark a Reading as DNF.
    """
    reading = Reading.objects.get(pk=reading_id)
    reading.mark_dnf()

    return JsonResponse({})


@login_required
def mark_edition_owned(request, edition_id):
    """Come here with a GET to mark a copy of an Edition of a Book as owned."""

    edition = Edition.objects.get(pk=edition_id)
    BookCopy(edition=edition, owner=request.user).save()

    return redirect("books:book_detail", book_id=edition.book.id)


@login_required
def mark_reading_started(request, edition_id):
    """Come here with a GET to mark an Edition of a Book as being started reading."""

    edition = Edition.objects.get(pk=edition_id)
    Reading(reader=request.user, edition=edition, start=timezone.now()).save()

    return redirect("books:book_detail", book_id=edition.book.id)


@login_required
def author_detail(request, author_id=None):
    """Detail view for an author."""

    author = Author.objects.get(pk=author_id)  # noqa

    context = {
        "author": author,
    }

    return render(request, "books/author_detail.html", context)
