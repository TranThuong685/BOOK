from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()

@register.filter
def intcomma_dot(value):
    return intcomma(value).replace(',', '.')
    
@register.filter
def times(value):
    return range(1,value+1)