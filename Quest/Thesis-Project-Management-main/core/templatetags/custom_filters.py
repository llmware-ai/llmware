from django import template

register = template.Library()

@register.filter(name='filter_attribute')
def filter_approval(projects, args):
    is_approved, is_rejected = args.split(',')
    is_approved = is_approved.lower() == 'true'
    is_rejected = is_rejected.lower() == 'true'

    if is_approved:
        return [project for project in projects if project.get('is_approved')]
    elif is_rejected:
        return [project for project in projects if project.get('is_rejected')]
    else:
        return [project for project in projects if not project.get('is_approved') and not project.get('is_rejected')]
