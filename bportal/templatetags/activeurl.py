from django import template

register = template.Library()

@register.filter(name='is_active_url')
@register.assignment_tag
def is_active_url(full_path, module_url):
    if full_path is not None:
        return full_path.startswith(module_url)
    else:
        return False
