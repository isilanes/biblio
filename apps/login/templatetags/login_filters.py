from django import template

register = template.Library()


@register.filter(name='add_class')
def add_class(value, arg):
    if isinstance(value, str):
        return ""

    return value.as_widget(attrs={'class': arg})
