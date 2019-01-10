from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render
from pybling.products import get_product

from core.models import UserProfile
from .forms import ProdutoForm
from .models import Produto


def product_view(request, codigo):
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


@login_required
def product_create(request, codigo):
    try:
        usuario = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        usuario = None

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

    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            new_product = form.save(commit=False)
            new_product.codigo = detalhes['codigo']
            new_product.descricao = detalhes['descricao']
            new_product.pago_na_china = detalhes['precoCusto']
            new_product.save()
            return redirect('product_view', codigo=codigo)

    else:
        form = ProdutoForm()

    return render(request, 'products/create.html', {'usuario': usuario,
                                                    'form': form,
                                                    'context': context})
