import plotly.graph_objects as go
from plotly.offline import plot as offplot


def get_book_progress_plot(points, longest=None):
    """Return <div> of Plotly plot area for book reading progress."""

    x_min = points[0][0]
    if longest:
        x_max = x_min + longest
    else:
        x_max = points[-1][0]

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
    figure.update_layout(xaxis_range=[x_min, x_max])

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
