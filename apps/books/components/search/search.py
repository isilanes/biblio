from django_components import register, Component
from django_components.component import DataType


@register("search")
class Search(Component):
    template_file = "search.html"
    css_file = "search.css"

    def get_context_data(self, form) -> DataType:
        return {
            "form": form,
        }
