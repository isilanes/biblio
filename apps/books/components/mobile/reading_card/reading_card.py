from django_components import Component, register


@register("reading_card")
class ReadingCard(Component):
    template_file = "reading_card.html"
    css_file = "reading_card.css"

    def get_context_data(self, reading):
        return {
            "reading": reading,
        }
