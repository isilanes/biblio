from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect

from . import core, statistics
from .models import Book, Author, BookStartEvent, Saga, BookEndEvent
from .forms import BookForm, AddBookForm, SearchBookForm


def index(request):
    """Index view."""

    context = {
        "currently_reading_books": currently_reading_books(),
        "currently_ordered_books": currently_ordered_books(),
        "already_read_books": already_read_books(),
    }

    return render(request, "books/index.html", context)


def sagas(request):
    """Saga view."""

    context = {
        "sagas": Saga.objects.all(),
        "completed": completed_sagas(),
        "owned": owned_sagas(),
        "missing": missing_sagas(),
    }

    return render(request, "books/sagas.html", context)


def book_detail(request, book_id):
    """Detail view for a book."""

    book = Book.objects.get(pk=book_id)

    reading = []  # list of (when, pages) for a time read
    readings = []  # one reading per time read
    for event in book.events:
        reading.append((event.when, event.page_equivalent))
        if event.page_equivalent == book.pages:
            readings.append(reading)
            reading = []
    if reading:
        readings.append(reading)

    # Longest reading:
    longest = None
    for reading in readings:
        dt = reading[-1][0] - reading[0][0]
        if longest is None or dt > longest:
            longest = dt

    context = {
        "book": book,
        "plotly_plots": [core.get_book_progress_plot(r, longest) for r in readings],
    }

    return render(request, "books/book_detail.html", context)


def update_book_progress(request, book_id):
    """Form to modify state of book."""

    book = Book.objects.get(pk=book_id)

    if request.method == "POST":
        form = BookForm(request.POST or None)
        if form.is_valid():
            pages_read = form.cleaned_data.get("pages_read")
            if pages_read is not None:
                if not book.is_currently_being_read:
                    book.mark_started()
                if pages_read > 0:
                    book.set_pages(pages_read)

                return redirect("books:book_detail", book_id=book_id)

    initial = {
        "pages_read": book.pages_read,
    }
    form = BookForm(initial=initial)

    context = {
        "form": form,
        "book": book,
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

                if "acquired" not in request.POST and "reading" not in request.POST:
                    book.owned = False

                if "ordered" in request.POST:
                    book.ordered = True

                # Saga info:
                saga_name = form.cleaned_data.get("saga")
                if saga_name:
                    try:
                        book.saga = Saga.objects.get(name=saga_name)
                    except ObjectDoesNotExist:
                        # Horrible hack to assign to new Saga object the first available id, because PostgreSQL
                        # at Heroku fails to assign an automatic one that is not duplicated if we simply do:
                        # saga = Saga(name=saga_name)
                        saga_id = 1
                        for saga_id in range(1, 10000):  # max try 10000 sagas
                            print("DEBUG105", saga_id)
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

                # Add started reading:
                if "reading" in request.POST:
                    start = BookStartEvent()
                    start.book = book
                    start.when = timezone.now()
                    start.save()

                return redirect("books:book_detail", book_id=book.id)

    initial = {
        "pages": 0,
        "year": 0,
        "saga": None,
        "index": None,
    }
    form = AddBookForm(initial=initial)
    context = {
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
    else:
        return handle_start_reading_get(request)


def mark_book_read(request, book_id):
    """Come here with a GET to mark a book read."""

    book = Book.objects.get(pk=book_id)
    book.mark_read()

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


def stats(request, year=None):
    """View with statistics for 'year'."""

    # If no year given, use current:
    if year is None:
        year = timezone.now().year

    state = statistics.State(year)

    pages_per_day = state.pages_per_day
    required_pages_per_day = state.required_pages_per_day

    try:
        ppd_perc = 100. * pages_per_day / (pages_per_day + required_pages_per_day)
    except ZeroDivisionError:
        ppd_perc = 0.0

    total_pages = 15000
    pages_per_book = 600
    perc_total_pages = 100. * state.pages_read / total_pages
    perc_ppb = 100. * state.pages_per_book / pages_per_book

    # Books read bar:
    blue_bar = state.book_percent_read
    if blue_bar >= 100.0:
        blue_bar = 100.0
        red_bar = 0
        green_bar = 0
    elif state.book_superavit > 0:
        red_bar = 0
        green_bar = state.book_superavit_percent
        blue_bar = blue_bar - green_bar
    else:
        red_bar = state.book_deficit_percent
        green_bar = 0

    books_read_bar = {
        "blue_bar": blue_bar,
        "red_bar": red_bar,
        "green_bar": green_bar,
    }

    # Expected books bar:
    if state.expected_books_by_end_of_year > state.GOAL:
        green_bar = 100. * state.expected_books_by_end_of_year / (2. * state.GOAL)
        blue_bar = 0
        red_bar = 0
    else:
        red_bar = 100. * state.expected_books_by_end_of_year / (2. * state.GOAL)
        blue_bar = 50. - red_bar
        green_bar = 0

    expected_books_bar = {
        "blue_bar": blue_bar,
        "red_bar": red_bar,
        "green_bar": green_bar,
    }

    context = {
        "year": year,
        "state": state,
        "books_read_bar": books_read_bar,
        "expected_books_bar": expected_books_bar,
        "currently_reading_books": currently_reading_books(),
        "pages_per_day": [pages_per_day, required_pages_per_day, ppd_perc, 100. - ppd_perc],
        "perc_total_pages": perc_total_pages,
        "perc_ppb": perc_ppb,
    }

    return render(request, "books/stats.html", context)


# Helper functions:
def currently_reading_books():
    """Return list of Books currently being read, unsorted."""

    book_states = {}

    start_events_query_set = BookStartEvent.objects.filter()
    started_books_query_set = Book.objects.filter(event__in=start_events_query_set)

    for book in started_books_query_set:
        book_states[book] = book_states.get(book, 0) + 1

    end_events_query_set = BookEndEvent.objects.all()
    finished_books_query_set = Book.objects.filter(event__in=end_events_query_set)

    for book in finished_books_query_set:
        book_states[book] = book_states.get(book, 0) - 1

    return [book for book, state in book_states.items() if state > 0]


def already_read_books():
    """Return list of books already read, sorted by finish date."""

    return [y for x, y in sorted([(book.date_read, book) for book in Book.objects.all()
                                  if book.is_already_read], reverse=True)]


def currently_ordered_books():
    """Return list of books currently ordered, but not yet received, unsorted."""

    return [book for book in Book.objects.all() if book.ordered]


def completed_sagas():
    return [s for s in Saga.objects.all() if s.completed]


def owned_sagas():
    return [s for s in Saga.objects.all() if not s.completed and s.owned]


def missing_sagas():
    """Sagas with one or more books missing."""

    return [s for s in Saga.objects.all() if not s.completed and not s.owned]


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
        "form": SearchBookForm(initial={"search_for": ""}),
        "matching_books": Book.objects.none(),
    }

    return render(request, "books/start_book.html", context)
