from datetime import timedelta

from django.utils import timezone
from django.db.models import Subquery, OuterRef
import plotly.graph_objects as go
from plotly.offline import plot as offplot

from .models import Book, BookStartEvent, BookEndEvent, Reading, ReadingUpdate


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


def currently_reading_books_by(user):
    """Return list of info about Books currently being read by 'user', unsorted."""

    book_states = {}

    start_events_query_set = BookStartEvent.objects.filter(user=user)
    started_books_query_set = Book.objects.filter(event__in=start_events_query_set)

    for book in started_books_query_set:
        book_states[book] = book_states.get(book, 0) + 1

    end_events_query_set = BookEndEvent.objects.filter(user=user)
    finished_books_query_set = Book.objects.filter(event__in=end_events_query_set)

    for book in finished_books_query_set:
        book_states[book] = book_states.get(book, 0) - 1

    return [(b, b.pages_read_by(user), b.percent_read_by(user)) for b, s in book_states.items() if s > 0]


def current_readings_by(user):
    latest_ru_subquery = ReadingUpdate.objects.filter(reading=OuterRef('id')).order_by("-date")[:1]

    return Reading.objects.filter(reader=user, end=None)\
        .annotate(pages_read=Subquery(latest_ru_subquery.values('page')))\
        .order_by("-start")


def completed_readings_by(user):
    """Return list of books already read, sorted by finish date."""

    return Reading.objects.filter(reader=user).exclude(end=None).order_by("-end")

