from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='times')
def times(number):
    return range(number)

@register.filter
def sub(value, arg):
    return value - arg

@register.filter
def zip_lists(list1, list2):
    return zip(list1, list2)

@register.filter
def get_attribute(obj, attr_name):
    return getattr(obj, attr_name, None)

@register.filter
def add_right_padding(value):
    if len(value) == 2:
        padded_value = f"{value}{'&nbsp;' * 9}"
        return mark_safe(padded_value)
    if len(value) == 3:
        padded_value = f"{value}{'&nbsp;' * 5}"
        return mark_safe(padded_value)
    else: return value