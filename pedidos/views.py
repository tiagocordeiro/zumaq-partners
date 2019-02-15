from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

from core.models import UserProfile, User
from .models import Pedido, PedidoItem
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
