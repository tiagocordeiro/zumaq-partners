from django.shortcuts import render


from pybling.products import get_product
from .models import Produto


def view_product(request, codigo):
    try:
        produto = Produto.objects.get(codigo=codigo)
        context = {'codigo': produto.codigo,
                   'descricao': produto.descricao,
                   'pago_na_china': produto.pago_na_china,
                   'reminmbi': produto.reminmbi,
                   'dolar_cotado': produto.dolar_cotado,
                   'impostos_na_china': produto.impostos_na_china,
                   'porcentagem_importacao': produto.porcentagem_importacao,
                   'coeficiente}': produto.coeficiente,
                   'product_status': 'no banco'}

    except Produto.DoesNotExist:
        produto = get_product(codigo=codigo)
        detalhes = produto.json()['retorno']['produtos'][0]['produto']
        context = {'codigo': detalhes['codigo'],
                   'descricao': detalhes['descricao'],
                   'pago_na_china': detalhes['precoCusto'],
                   'reminmbi': '',
                   'dolar_cotado': '',
                   'impostos_na_china': '',
                   'porcentagem_importacao': '',
                   'coeficiente': '',
                   'product_status': 'no bling'}

    return render(request, 'products/product.html', context)
