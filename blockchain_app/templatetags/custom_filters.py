from django import template

register = template.Library()

@register.filter
def sum_attr(queryset, attr_name):
    """Tính tổng một thuộc tính của queryset"""
    try:
        return sum(getattr(obj, attr_name, 0) or 0 for obj in queryset)
    except (TypeError, AttributeError):
        return 0

@register.filter
def average_attr(queryset, attr_name):
    """Tính trung bình một thuộc tính của queryset"""
    try:
        total = sum(getattr(obj, attr_name, 0) or 0 for obj in queryset)
        count = sum(1 for obj in queryset if getattr(obj, attr_name, None) is not None)
        return total / count if count > 0 else None
    except (TypeError, AttributeError):
        return None

@register.filter
def multiply(value, arg):
    return value * arg
    
@register.filter
def divide(value, arg):
    if arg == 0:
        return 0
    return value / arg