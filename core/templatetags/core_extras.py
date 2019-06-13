from unicodedata import normalize

from django import template

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@register.filter(name='subtotal')
def subtotal(valor_un, quantidade):
    return valor_un * quantidade


@register.filter(name='normalize_for_table')
def normalize_for_table(text):
    return normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')


@register.filter(name='load_thumb')
def load_thumb(image_url):
    return image_url.replace('800x800', '100x100')
