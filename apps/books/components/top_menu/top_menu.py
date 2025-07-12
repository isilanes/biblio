from django_components import Component, register


@register("top_menu")
class TopMenu(Component):
    template_file = "top_menu.html"
    css_file = "top_menu.css"

    def get_context_data(self, user) -> dict:
        return {
            "user": user,
        }
