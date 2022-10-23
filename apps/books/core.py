from datetime import timedelta

from django.utils import timezone
from django.db.models.functions import Coalesce
from django.db.models import Subquery, OuterRef, F
import plotly.graph_objects as go
from plotly.offline import plot as offplot

from biblio.core import as_float
from .models import Reading, ReadingUpdate, Saga, Edition


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

    open_readings = Reading.objects.filter(reader=user, end=None)
    Edition.objects.filter(reading__in=open_readings, pages=0).update(pages=1)  # just in case

    return open_readings.annotate(
        pages_read=Coalesce(Subquery(latest_ru_subquery.values('page')), 0)
    ).annotate(
        fraction_read=as_float(F('pages_read')) / as_float(F('edition__pages'))
    ).annotate(
        percent_read=as_float(F('fraction_read')) * 100.,
    ).order_by("-start")


def completed_readings_by_year_for(user):
    """
    Return list of books already read, sorted by finish date and grouped by year (recent first).
    """
    my_readings = Reading.objects.filter(reader=user).exclude(end=None)

    years_with_readings_qs = my_readings.order_by("-end__year").values_list(
        "end__year",
        flat=True,
    ).distinct()

    data = []
    for year in years_with_readings_qs:
        readings = my_readings.filter(end__year=year).order_by("-end")

        if readings:
            data.append({"year": year, "readings": readings})

    return data


def get_saga_data_for(user):
    sagas = {
        "read": [],
        "owned": [],
        "not_owned": [],
    }
    for saga in Saga.objects.order_by("name"):
        saga_item = {
            "name": saga.name,
            "books": [],
            "is_completed": True,
            "is_owned": True,
        }

        for book in saga.books:
            book_read = book.is_already_read_by(user)
            book_owned = book.is_owned_by(user)

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

        if saga_item["is_completed"]:
            sagas["read"].append(saga_item)
        elif saga_item["is_owned"]:
            sagas["owned"].append(saga_item)
        else:
            sagas["not_owned"].append(saga_item)

    return sagas
