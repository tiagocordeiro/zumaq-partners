from django.shortcuts import redirect, render
from django.contrib import messages
from django.urls import reverse

from core.models import UserProfile, User
from .models import Pedido, PedidoItem
from .forms import PedidoForm, PedidoItensForm
from django.forms.models import inlineformset_factory
from products.models import Produto, CustomCoeficiente, CustomCoeficienteItens


def pedido_add_item(request, **kwargs):
    try:
        usuario = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        usuario = None

    parceiro = User.objects.get(username=request.user)
    
    produto = Produto.objects.get(codigo=kwargs.get('codigo'))
    print(produto.codigo, produto.descricao)
    
    pedido = Pedido.objects.filter(parceiro=parceiro, status=0).first()
    if pedido is None:
        pedido = Pedido.objects.create(parceiro=parceiro)

    try:
        custom_coeficiente = CustomCoeficiente.objects.get(parceiro=parceiro)
        custom_prices = CustomCoeficienteItens.objects.all().filter(parceiro=custom_coeficiente)
        parceiro_coeficiente = custom_coeficiente.coeficiente_padrao

        try:
            c_price = custom_prices.filter(produto__codigo=produto.codigo).values('coeficiente')[0]['coeficiente']
            if c_price:
                produto.cliente_paga = round(produto.cliente_paga() + (produto.cliente_paga() * c_price),
                                             ndigits=2)
        except IndexError:
            produto.cliente_paga = round(produto.cliente_paga() + (produto.cliente_paga() * parceiro_coeficiente),
                                         ndigits=2)

    except CustomCoeficiente.DoesNotExist:
        produto.cliente_paga = round(produto.cliente_paga() + (produto.cliente_paga() * parceiro_coeficiente),
                                     ndigits=2)

    PedidoItem.objects.create(pedido=pedido, item=produto, valor_unitario=produto.cliente_paga)
        
    pedido.save()

    messages.info(request, f"{produto.descricao} adicionado ao pedido...")
    return redirect(reverse('product_list'))


def pedido_aberto(request):
    parceiro = User.objects.get(username=request.user)
    pedido = Pedido.objects.filter(parceiro=parceiro, status=0).first()
    if pedido is None:
        pedido_vazio = "Seu pedido está vazio"
        return render(request, 'pedidos/pedido_aberto.html', {'parceiro': parceiro,
                                                              'pedido_vazio': pedido_vazio})

    pedido_itens = PedidoItem.objects.all().filter(pedido__exact=pedido)
    pedido_total = 0
    for item in pedido_itens:
        subtotal = item.quantidade * item.valor_unitario
        pedido_total = pedido_total + subtotal

    itens_pedido_formset = inlineformset_factory(
        Pedido, PedidoItem, form=PedidoItensForm, extra=0, can_delete=True)

    if request.method == 'POST':
        form = PedidoForm(request.POST, instance=pedido, prefix='main')
        formset = itens_pedido_formset(request.POST, instance=pedido, prefix='product')

        try:
            if form.is_valid() and formset.is_valid():
                form.save()
                formset.save()
                messages.success(request, "Pedido atualizado")
                return redirect(pedido_aberto)
        except Exception as e:
            messages.warning(request, 'Ocorreu um erro ao atualizar: {}'.format(e))

    else:
        form = PedidoForm(instance=pedido, prefix='main')
        formset = itens_pedido_formset(instance=pedido, prefix='product')

    return render(request, 'pedidos/pedido_aberto.html', {'parceiro': parceiro,
                                                          'pedido': pedido,
                                                          'pedido_itens': pedido_itens,
                                                          'pedido_total': pedido_total,
                                                          'form': form,
                                                          'formset': formset})

def pedido_checkout(request):
    pass
