from django import template
from datetime import datetime

register = template.Library()

@register.filter
def is_date_format(value, date_format="%Y-%m-%d"): 
    if value:   
        try:
            datetime.strptime(value, date_format)
            return True
        except ValueError:
            return False
    return False


@register.filter
def format_date(value):
    return value.strftime('%Y-%m-%d')
