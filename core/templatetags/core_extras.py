import locale
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


@register.filter(name='currency_display')
def currency_display(valor):
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    valor = locale.currency(valor, grouping=True, symbol=None)
    return valor


@register.filter(name='tributos')
def tributos(valor):
    tributo = valor / 100 * 3
    return tributo


@register.filter(name='total_com_tributos')
def total_com_tributos(valor):
    total_tributado = valor + (valor / 100 * 3)
    return total_tributado
