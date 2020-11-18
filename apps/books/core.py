from datetime import timedelta

from django.utils import timezone
from django.db.models.functions import Coalesce
from django.db.models import Subquery, OuterRef, F, Case, When, Value, BooleanField, Count
import plotly.graph_objects as go
from plotly.offline import plot as offplot

from biblio.core import as_float, TicToc
from .models import Reading, ReadingUpdate, Saga, Book


def get_book_progress_plot(points, total_pages, longest=0, pages_per_day=None):
    """Return <div> of Plotly plot area for book reading progress."""

    # This reading ends with book finished if...
    finished = points[-1][1] == total_pages

    # Limits in X:
    x_min = points[0][0]
    x_max = max(points[-1][0], x_min + longest)

    scatter_x, scatter_y = zip(*points)

    plot_trace = go.Scatter(x=scatter_x,
                            y=scatter_y,
                            mode='lines+markers',
                            marker={
                                "size": 10,
                                "color": 'rgba(0, 0, 200, 1.0)',
                            },
                            hoverinfo='x+y')

    figure = go.Figure(data=[plot_trace])

    if not finished:
        x_wish, y_wish, labels = [], [], []
        for i in range(1, len(scatter_x)):
            x_wish.append(scatter_x[i])
            elapsed_days = (scatter_x[i] - scatter_x[i - 1]).total_seconds() / 86400.
            expected_new_pages_read = pages_per_day * elapsed_days
            new_y = scatter_y[i - 1] + expected_new_pages_read
            y_wish.append(new_y)
            labels.append(f"{new_y:.1f}")

        now_x = timezone.now()
        now_y = scatter_y[-1] + pages_per_day * (now_x - scatter_x[-1]).total_seconds() / 86400.
        x_wish.append(now_x)
        y_wish.append(now_y)
        labels.append(f"{now_y:.1f}")

        wish_trace = go.Scatter(x=x_wish,
                                y=y_wish,
                                mode='lines+text',
                                marker={
                                    "size": 10,
                                    "color": 'rgba(0, 0, 200, 1.0)',
                                },
                                line={
                                    "color": 'green',
                                    "dash": "dash",
                                },
                                text=labels,
                                textposition="top right",
                                hoverinfo='x+y')

        figure.add_trace(wish_trace)

        x_max = max(x_max, now_x + timedelta(hours=12))

    figure.update_layout(xaxis_range=[x_min, x_max], showlegend=False)

    config = {
        "displayModeBar": True,
        "modeBarButtons": [
            ["resetScale2d"],
            ["zoom2d"],
            ["lasso2d"],
            ["pan2d"],
        ],
        "scrollZoom": False,
    }

    return offplot(figure, output_type="div", include_plotlyjs=False, config=config)


def current_readings_by(user):
    latest_ru_subquery = ReadingUpdate.objects.filter(reading=OuterRef('id')).order_by("-date")[:1]

    return Reading.objects.filter(reader=user, end=None)\
        .annotate(pages_read=Coalesce(Subquery(latest_ru_subquery.values('page')), 0))\
        .annotate(fraction_read=as_float(F('pages_read')) / as_float(F('book__pages'))) \
        .annotate(percent_read=as_float(F('fraction_read')) * 100.)\
        .order_by("-start")


def completed_readings_by_year_for(user):
    """Return list of books already read, sorted by finish date and grouped by year (recent first)."""

    years_with_readings_qs = Reading.objects.filter(reader=user).exclude(end=None)\
        .order_by("-end__year")\
        .values("end__year")\
        .distinct()

    data = []
    for year in [v["end__year"] for v in years_with_readings_qs]:
        year_data = {
            "year": year,
            "readings": Reading.objects.filter(reader=user, end__year=year).order_by("-end"),
        }
        data.append(year_data)

    return data


def get_saga_data_for(user):
    tt = TicToc()
    catch_unreads_sq = Book.objects\
        .filter(saga=OuterRef("id"))\
        .exclude(reading__reader=user, reading__end__isnull=False)\
        .annotate(is_unread=Case(When(title__isnull=False,  # in other words, always
                                      then=Value(True)), output_field=BooleanField()))[:1]

    # This is wrong. Must change to "owned by user", not just "owned". Requires rewriting elsewhere.
    catch_unowneds_sq = Book.objects\
        .filter(saga=OuterRef("id"))\
        .filter(owned=False)\
        .annotate(is_unowned=Case(When(title__isnull=False,  # in other words, always
                                       then=Value(True)), output_field=BooleanField()))[:1]

    sagas = Saga.objects\
        .annotate(has_unreads=Coalesce(Subquery(catch_unreads_sq.values('is_unread')), False))\
        .annotate(has_unowneds=Coalesce(Subquery(catch_unowneds_sq.values('is_unowned')), False))

    data = {
        "completed": sagas.filter(has_unreads=False),  # sagas with no unread book
        "owned": sagas.filter(has_unowneds=False, has_unreads=True),  # no unowned AND at least some unread book
        "missing": sagas.filter(has_unreads=True, has_unowneds=True),  # at least some unowned AND some unread books
    }
    tt.toc("data")

    sagas = []
    for saga in Saga.objects.order_by("name"):
        saga_item = {
            "name": saga.name,
            "books": [],
            "is_completed": True,
            "is_owned": True,
        }

        for book in saga.books:
            book_read = book.is_already_read_by(user)
            book_owned = True

            if not book_read:
                saga_item["is_completed"] = False

            if not book_owned:
                saga_item["is_owned"] = False

            status = "not-owned"
            if book_read:
                status = "read"
            elif book_owned:
                status = "owned"

            book_item = (book, status)
            saga_item["books"].append(book_item)

        sagas.append(saga_item)

    tt.toc("data2")

    return data, sagas
