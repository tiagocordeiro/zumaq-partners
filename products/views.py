from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render
from pybling.products import get_product

from core.models import UserProfile
from .forms import ProdutoForm
from .models import Produto


@login_required
def product_view(request, codigo):
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
                   'coeficiente': produto.coeficiente,
                   'product_status': 'no banco'}

    except Produto.DoesNotExist:
        return redirect('product_create', codigo=codigo)

    return render(request, 'products/product.html', {'context': context,
                                                     'produto': produto,
                                                     'usuario': usuario})


@login_required
def product_create(request, codigo):
    try:
        usuario = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        usuario = None

    try:
        produto = Produto.objects.get(codigo=codigo)
        return redirect('product_update', codigo=produto.codigo)

    except Produto.DoesNotExist:
        try:
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
        except KeyError:
            return redirect('product_add')

    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            new_product = form.save(commit=False)
            new_product.codigo = detalhes['codigo']
            new_product.descricao = detalhes['descricao']
            new_product.pago_na_china = detalhes['precoCusto']
            new_product.save()
            return redirect('product_update', codigo=codigo)

    else:
        form = ProdutoForm()

    return render(request, 'products/create.html', {'usuario': usuario,
                                                    'form': form,
                                                    'context': context})


@login_required
def product_update(request, codigo):
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
                   'product_status': 'no banco',
                   'produto': produto}

    except Produto.DoesNotExist:
        return redirect('product_create', codigo=codigo)

    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            return redirect('product_view', codigo=codigo)

    else:
        form = ProdutoForm(instance=produto)

    return render(request, 'products/update.html', {'usuario': usuario,
                                                    'form': form,
                                                    'produto': produto,
                                                    'context': context})


@login_required
def product_add(request):
    if request.method == 'POST':
        codigo = request.POST['codigo_do_bling']
        return redirect('product_create', codigo=codigo)

    return render(request, 'products/add.html')


@login_required
def product_list(request):
    try:
        usuario = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        usuario = None

    produtos = Produto.objects.all()

    return render(request, 'products/list.html', {'usuario': usuario,
                                                  'produtos': produtos})
