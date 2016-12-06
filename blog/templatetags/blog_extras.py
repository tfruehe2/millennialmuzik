from django import template

register = template.Library()

@register.filter(name="get_post")
def get_post(value):
    return value.post

@register.filter
def sort_by(queryset, order):
    return queryset.order_by(order)
