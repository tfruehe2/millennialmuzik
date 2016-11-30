from django import template

register = template.Library()

@register.filter(name="get_post")
def get_post(value):
    return value.post
