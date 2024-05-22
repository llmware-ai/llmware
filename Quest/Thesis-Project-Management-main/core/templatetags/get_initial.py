from django import template

register = template.Library()


@register.filter(name='get_initial')
def get_initial(name):
    return (name.first_name[0] + name.last_name[0]).upper()
