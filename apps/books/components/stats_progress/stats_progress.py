from django_components import Component, register

from apps.books.statistics import State


@register("stats_progress")
class StatsProgress(Component):
    template_file = "stats_progress.html"
    css_file = "stats_progress.css"

    def get_context_data(self, state: State) -> dict:
        return {
            "state": state,
        }
