from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.forms.models import inlineformset_factory
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from pybling.products import get_product

from core.models import UserProfile, User
from pedidos.models import Pedido, PedidoItem
from .facade import get_partner_prices, get_partner_price
from .forms import ProdutoForm, ProdutoAtacadoForm
from .models import Produto, CustomCoeficiente, CustomCoeficienteItens, ProdutoAtacado, BlockedProducts, WaitingList


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
            imagens = detalhes['imagem']
            if imagens:
                imagem = imagens[0]['link']
            else:
                imagem = None
            context = {'codigo': detalhes['codigo'],
                       'descricao': detalhes['descricao'],
                       'pago_na_china': detalhes['precoCusto'],
                       'reminmbi': '',
                       'dolar_cotado': '',
                       'impostos_na_china': '',
                       'porcentagem_importacao': '',
                       'coeficiente': '',
                       'product_status': 'no bling',
                       'imagem': imagem, }
        except KeyError:
            return redirect('product_add')

    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            new_product = form.save(commit=False)
            new_product.codigo = detalhes['codigo']
            new_product.descricao = detalhes['descricao']
            new_product.pago_na_china = detalhes['precoCusto']
            new_product.imagem = imagem
            new_product.save()
            messages.success(request, "Produto cadastrado.")
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

    try:
        produto_atacado = ProdutoAtacado.objects.all().filter(produto=produto)
    except ProdutoAtacado.DoesNotExist:
        produto_atacado = None

    produto_atacado_formset = inlineformset_factory(
        Produto, ProdutoAtacado, form=ProdutoAtacadoForm, extra=0, can_delete=True)

    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto, prefix='main')
        formset = produto_atacado_formset(request.POST, instance=produto, prefix='product')

        try:
            if form.is_valid() and formset.is_valid():
                form.save()
                formset.save()
                messages.success(request, "Produto atualizado.")
                return redirect('product_update', codigo=codigo)

        except Exception as e:
            messages.warning(request, 'Ocorreu um erro ao atualizar: {}'.format(e))

    else:
        form = ProdutoForm(instance=produto, prefix='main')
        formset = produto_atacado_formset(instance=produto, prefix='product')

    return render(request, 'products/update.html', {'usuario': usuario,
                                                    'form': form,
                                                    'formset': formset,
                                                    'produto': produto,
                                                    'produto_atacado': produto_atacado,
                                                    'context': context})


@login_required
def product_add(request):
    if request.method == 'POST':
        codigo = request.POST['codigo_do_bling']
        return redirect('product_create', codigo=codigo)

    return render(request, 'products/add.html')


def api_product_list(request, secret_key):
    perfil_parceiro = get_object_or_404(UserProfile, api_secret_key=secret_key)
    parceiro = User.objects.get(username=perfil_parceiro.user.username)

    bloqueados = BlockedProducts.objects.filter(parceiro__parceiro=parceiro).values_list('produto__codigo')
    produtos = Produto.objects.all().order_by('descricao').exclude(codigo__in=bloqueados)

    partner_prices = get_partner_prices(parceiro, produtos)

    data = {"results": partner_prices}
    return JsonResponse(data)


def api_product_detail(request, codigo, secret_key):
    perfil_parceiro = get_object_or_404(UserProfile, api_secret_key=secret_key)
    parceiro = User.objects.get(username=perfil_parceiro.user.username)
    produto = get_object_or_404(Produto, codigo=codigo)
    bloqueados = BlockedProducts.objects.filter(parceiro__parceiro=parceiro)
    bloqueados_list = []

    for item in bloqueados:
        bloqueados_list.append(item.produto.codigo)

    if produto.codigo in bloqueados_list:
        response = JsonResponse({"status": "false", "message": "Produto não disponível"}, status=403)
        return response

    data = {"results": {
        "codigo": produto.codigo,
        "descricao": produto.descricao,
        "estoque": produto.active,
        "valor": get_partner_price(parceiro, produto)
    }}
    return JsonResponse(data)


def api_product_list_header_token(request):
    try:
        secret_key = request.headers["Token"]
        perfil_parceiro = get_object_or_404(UserProfile, api_secret_key=secret_key)
        parceiro = User.objects.get(username=perfil_parceiro.user.username)

        bloqueados = BlockedProducts.objects.filter(parceiro__parceiro=parceiro).values_list('produto__codigo')
        produtos = Produto.objects.all().order_by('descricao').exclude(codigo__in=bloqueados)

        partner_prices = get_partner_prices(parceiro, produtos)

        data = {"results": partner_prices}
        return JsonResponse(data)
    except KeyError:
        response = JsonResponse({"status": "false", "message": "Token não informado"}, status=500)
        return response


def api_product_detail_header_token(request, codigo):
    try:
        secret_key = request.headers["Token"]
        perfil_parceiro = get_object_or_404(UserProfile, api_secret_key=secret_key)
        parceiro = User.objects.get(username=perfil_parceiro.user.username)
        produto = get_object_or_404(Produto, codigo=codigo)
        bloqueados = BlockedProducts.objects.filter(parceiro__parceiro=parceiro)
        bloqueados_list = []

        for item in bloqueados:
            bloqueados_list.append(item.produto.codigo)

        if produto.codigo in bloqueados_list:
            response = JsonResponse({"status": "false", "message": "Produto não disponível"}, status=403)
            return response

        data = {"results": {
            "codigo": produto.codigo,
            "descricao": produto.descricao,
            "estoque": produto.active,
            "valor": get_partner_price(parceiro, produto)
        }}
        return JsonResponse(data)
    except KeyError:
        response = JsonResponse({"status": "false", "message": "Token não informado"}, status=500)
        return response


@login_required
def product_list_json(request):
    parceiro = User.objects.get(username=request.user)
    bloqueados = BlockedProducts.objects.filter(parceiro__parceiro=parceiro).values_list('produto__codigo')
    produtos = Produto.objects.all().order_by('descricao').exclude(codigo__in=bloqueados)

    partner_prices = get_partner_prices(parceiro, produtos)

    data = {"results": partner_prices}
    return JsonResponse(data)


@login_required
def product_detail_json(request, codigo):
    produto = get_object_or_404(Produto, codigo=codigo)
    parceiro = User.objects.get(username=request.user)
    bloqueados = BlockedProducts.objects.filter(parceiro__parceiro=parceiro)
    bloqueados_list = []

    for item in bloqueados:
        bloqueados_list.append(item.produto.codigo)

    if produto.codigo in bloqueados_list:
        response = JsonResponse({"status": "false", "message": "Produto não disponível"}, status=403)
        return response

    data = {"results": {
        "codigo": produto.codigo,
        "descricao": produto.descricao,
        "estoque": produto.active,
        "valor": get_partner_price(parceiro, produto)
    }}
    return JsonResponse(data)


@login_required
def product_list(request):
    try:
        usuario = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        usuario = None

    parceiro = User.objects.get(username=request.user)
    user = User.objects.get(username=request.user)

    if user.groups.filter(name='Gerente').exists():
        produtos = Produto.objects.all().order_by('descricao')
    else:
        bloqueados = BlockedProducts.objects.filter(parceiro__parceiro=parceiro).values_list('produto__codigo')
        produtos = Produto.objects.all().filter(active=True).order_by('descricao').exclude(codigo__in=bloqueados)

    total_produtos = len(produtos)

    # TODO: Separar lógica de negócio

    try:
        custom_coeficiente = CustomCoeficiente.objects.get(parceiro=parceiro)
        custom_prices = CustomCoeficienteItens.objects.all().filter(parceiro=custom_coeficiente)
        parceiro_coeficiente = custom_coeficiente.coeficiente_padrao

        for produto in produtos:
            try:
                c_price = custom_prices.filter(produto__codigo=produto.codigo).values('coeficiente')[0]['coeficiente']
                if c_price:
                    produto.cliente_paga = round(produto.cliente_paga() + (produto.cliente_paga() * c_price),
                                                 ndigits=2)
                    produto.coeficiente = c_price
            except IndexError:
                produto.cliente_paga = round(produto.cliente_paga() + (produto.cliente_paga() * parceiro_coeficiente),
                                             ndigits=2)

    except CustomCoeficiente.DoesNotExist:
        pass

    if total_produtos == 1:
        total_str = f"Encontrado {total_produtos} produto"
    elif total_produtos == 0:
        total_str = "Nenhum produto cadastrado"
    else:
        total_str = f"Encontrados {total_produtos} produtos"

    parceiro = User.objects.get(username=request.user)

    pedido = Pedido.objects.filter(parceiro=parceiro, status=0).first()
    if pedido is None:
        pedido_itens_qt = 0
    else:
        pedido_itens_qt = PedidoItem.objects.filter(pedido=pedido).count()

    return render(request, 'products/list.html', {'usuario': usuario,
                                                  'produtos': produtos,
                                                  'total_str': total_str,
                                                  'pedido_itens_qt': pedido_itens_qt})


@login_required
def product_atacado_list(request):
    try:
        usuario = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        usuario = None

    parceiro = User.objects.get(username=request.user)
    user = User.objects.get(username=request.user)
    if user.groups.filter(name='Gerente').exists():
        pass
    else:
        return redirect('dashboard')

    if user.groups.filter(name='Gerente').exists():
        produtos = ProdutoAtacado.objects.all().order_by('produto__descricao', 'coeficiente')
    else:
        bloqueados = BlockedProducts.objects.filter(parceiro__parceiro=parceiro).values_list('produto__codigo')
        produtos = ProdutoAtacado.objects.all().filter(
            produto__active=True).order_by('produto__descricao', 'coeficiente').exclude(produto__codigo__in=bloqueados)

    total_produtos = len(produtos)

    # TODO: Separar lógica de negócio

    for produto in produtos:
        produto.cliente_paga = round(
            produto.produto.custo_da_peca() + (produto.coeficiente * produto.produto.custo_da_peca()), ndigits=2)
        produto.total = produto.cliente_paga * produto.quantidade
        produto.unitario_em_dolar = round(produto.cliente_paga / produto.produto.dolar_cotado, ndigits=2)

    if total_produtos == 1:
        total_str = f"Encontrado {total_produtos} produto"
    elif total_produtos == 0:
        total_str = "Nenhum produto cadastrado"
    else:
        total_str = f"Encontrados {total_produtos} produtos"

    pedido = Pedido.objects.filter(parceiro=parceiro, status=0).first()
    if pedido is None:
        pedido_itens_qt = 0
    else:
        pedido_itens_qt = PedidoItem.objects.filter(pedido=pedido).count()

    return render(request, 'products/list_atacado.html', {'usuario': usuario,
                                                          'produtos': produtos,
                                                          'total_str': total_str,
                                                          'pedido_itens_qt': pedido_itens_qt})


@login_required
def waitinglist(request):
    if request.user.groups.filter(name='Gerente').exists():
        return redirect('waitinglist_admin')

    try:
        usuario = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        usuario = None

    parceiro = User.objects.get(username=request.user)

    pedido = Pedido.objects.filter(parceiro=parceiro, status=0).first()
    if pedido is None:
        pedido_itens_qt = 0
    else:
        pedido_itens_qt = PedidoItem.objects.filter(pedido=pedido).count()

    waitinglist_items = WaitingList.objects.filter(parceiro=parceiro)
    return render(request, 'products/waitinglist.html', {'parceiro': parceiro,
                                                         'usuario': usuario,
                                                         'pedido_itens_qt': pedido_itens_qt,
                                                         'waitinglist_items': waitinglist_items})


@login_required
def add_item_to_waitinglist(request, codigo):
    parceiro = User.objects.get(username=request.user)
    bloqueados = BlockedProducts.objects.filter(parceiro__parceiro=parceiro)
    bloqueados_list = []

    for item in bloqueados:
        bloqueados_list.append(item.produto.codigo)

    produto = Produto.objects.get(codigo=codigo)
    if produto.codigo in bloqueados_list:
        messages.info(request, f'{produto.descricao} Não está disponível para encomenda.')
        return redirect(reverse('product_list'))

    if produto.fora_de_estoque is False:
        messages.info(request, f'{produto.descricao} Está disponível para pedido.'
                               f'Por isso não pode ser adicionado a lista de espera')
        return redirect(reverse('product_list'))

    try:
        WaitingList.objects.create(parceiro=parceiro, produto=produto)

    except IntegrityError:
        messages.info(request,
                      f'{produto.descricao} já está na lista de espera... '
                      f'<a href="{reverse("waitinglist")}" class="alert-link">Ver lista</a>.')
        return redirect(reverse('product_list'))

    messages.info(request,
                  f'{produto.descricao} adicionado a lista de easpera... '
                  f'<a href="{reverse("waitinglist")}" class="alert-link">Ver lista</a>.')
    return redirect(reverse('product_list'))


@login_required
def remove_from_waitinglist(request, codigo):
    parceiro = User.objects.get(username=request.user)
    produto = Produto.objects.get(codigo=codigo)

    item = WaitingList.objects.get(parceiro=parceiro, produto=produto)
    item.delete()

    messages.info(request, f'{produto.descricao} Foi removido da lista.')
    return redirect(reverse('waitinglist'))


@login_required
def waitinglist_admin(request):
    try:
        usuario = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        usuario = None

    # Check access role
    usuario_gerente = User.objects.get(username=request.user)
    if usuario_gerente.groups.filter(name='Gerente').exists():
        pass
    else:
        return redirect('dashboard')

    waitinglist_data = []
    waitinglist_produtos = WaitingList.objects.distinct('produto')
    for produto in waitinglist_produtos:
        parceiros = list(
            WaitingList.objects.values('parceiro__username', 'parceiro__email').filter(produto=produto.produto))
        waitinglist_item = dict({'produto': produto, 'parceiros': parceiros})
        waitinglist_data.append(waitinglist_item)

    return render(request, 'products/waitinglist_admin.html', {'usuario': usuario,
                                                               'waitinglist_data': waitinglist_data})
