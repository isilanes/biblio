from django import template


register = template.Library()


@register.filter
def absolute(value):
    return abs(float(value))

@register.filter
def wrt_fifty(value: float) -> float:
    """
    Given a 'value' "deviation" from 50%, return the final percentage.

    Args:
        value (float): The deviation from 50%.

    Returns:
        float: The final percentage value.
    """
    return 50 + value/2
