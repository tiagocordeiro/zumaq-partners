import os
import ssl

from decouple import config
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.forms.models import inlineformset_factory
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import get_template
from django.urls import reverse
from django.utils.html import strip_tags
from xhtml2pdf import pisa

from core.models import UserProfile, User
from products.models import Produto, CustomCoeficiente, CustomCoeficienteItens, ProdutoAtacado
from .forms import PedidoForm, PedidoItensForm
from .models import Pedido, PedidoItem


@login_required
def pedido_add_item(request, **kwargs):
    parceiro = User.objects.get(username=request.user)

    produto = Produto.objects.get(codigo=kwargs.get('codigo'))

    pedido = Pedido.objects.filter(parceiro=parceiro, status=0).first()
    if pedido is None:
        pedido = Pedido.objects.create(parceiro=parceiro)

    if pedido.pedidoitem_set.all().filter(item=produto).exists():
        messages.info(request,
                      f'{produto.descricao} Já está no pedido. '
                      f'<a href="{reverse("pedido_aberto")}" class="alert-link">Ver pedido</a>.')
        return redirect(reverse('product_list'))

    try:
        custom_coeficiente = CustomCoeficiente.objects.get(parceiro=parceiro)
        custom_prices = CustomCoeficienteItens.objects.all().filter(parceiro=custom_coeficiente)
        parceiro_coeficiente = custom_coeficiente.coeficiente_padrao

        try:
            c_price = custom_prices.filter(produto__codigo=produto.codigo).values('coeficiente')[0]['coeficiente']
            if c_price == 0:
                produto.cliente_paga = produto.cliente_paga()
            else:
                produto.cliente_paga = round(produto.cliente_paga() + (produto.cliente_paga() * c_price), ndigits=2)

        except IndexError:
            produto.cliente_paga = round(produto.cliente_paga() + (produto.cliente_paga() * parceiro_coeficiente),
                                         ndigits=2)

    except CustomCoeficiente.DoesNotExist:
        produto.cliente_paga = round(produto.cliente_paga() + (produto.cliente_paga() * parceiro_coeficiente),
                                     ndigits=2)

    PedidoItem.objects.create(pedido=pedido, item=produto, valor_unitario=produto.cliente_paga)

    pedido.save()

    messages.info(request,
                  f'{produto.descricao} adicionado ao pedido... '
                  f'<a href="{reverse("pedido_aberto")}" class="alert-link">Ver pedido</a>.')
    return redirect(reverse('product_list'))


@login_required
def pedido_add_item_atacado(request, **kwargs):
    parceiro = User.objects.get(username=request.user)
    user = User.objects.get(username=request.user)
    if user.groups.filter(name='Gerente').exists():
        pass
    else:
        return redirect('dashboard')

    produto = Produto.objects.get(codigo=kwargs.get('codigo'))
    quantidade = kwargs.get('quantidade')
    produto_atacado = ProdutoAtacado.objects.get(produto=produto, quantidade=quantidade)
    quantidade = produto_atacado.quantidade

    pedido = Pedido.objects.filter(parceiro=parceiro, status=0).first()
    if pedido is None:
        pedido = Pedido.objects.create(parceiro=parceiro)

    if pedido.pedidoitem_set.all().filter(item=produto).exists():
        messages.info(request,
                      f'{produto.descricao} Já está no pedido. '
                      f'<a href="{reverse("pedido_aberto")}" class="alert-link">Ver pedido</a>.')
        return redirect(reverse('product_list_atacado'))

    custo_da_peca = produto.custo_da_peca()
    valor_unitario = round(custo_da_peca + (produto_atacado.coeficiente * custo_da_peca), ndigits=2)

    PedidoItem.objects.create(pedido=pedido,
                              item=produto,
                              valor_unitario=valor_unitario,
                              quantidade=quantidade,
                              atacado=True)

    pedido.save()

    messages.info(request,
                  f'{produto.descricao} adicionado ao pedido... '
                  f'<a href="{reverse("pedido_aberto")}" class="alert-link">Ver pedido</a>.')
    return redirect(reverse('product_list_atacado'))


@login_required
def pedido_aberto(request):
    try:
        usuario = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        usuario = None

    parceiro = User.objects.get(username=request.user)
    pedido = Pedido.objects.filter(parceiro=parceiro, status=0).first()
    if pedido is None:
        pedido_itens_qt = 0
        return render(request, 'pedidos/pedido_aberto.html', {'parceiro': parceiro,
                                                              'pedido_itens_qt': pedido_itens_qt})

    pedido_itens = PedidoItem.objects.all().filter(pedido__exact=pedido)
    pedido_total = 0
    for item in pedido_itens:
        subtotal = item.quantidade * item.valor_unitario
        pedido_total = pedido_total + subtotal

    itens_pedido_formset = inlineformset_factory(
        Pedido, PedidoItem, form=PedidoItensForm, extra=0, can_delete=True)

    pedido_itens_qt = PedidoItem.objects.filter(pedido=pedido).count()

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
                                                          'usuario': usuario,
                                                          'pedido': pedido,
                                                          'pedido_itens': pedido_itens,
                                                          'pedido_total': pedido_total,
                                                          'pedido_itens_qt': pedido_itens_qt,
                                                          'form': form,
                                                          'formset': formset})


@login_required
def pedido_checkout(request, pk):
    try:
        usuario = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        usuario = None

    parceiro = User.objects.get(username=request.user)
    pedido = Pedido.objects.get(pk=pk)

    if pedido.parceiro != parceiro:
        return redirect('dashboard')

    pedido_itens = PedidoItem.objects.all().filter(pedido__exact=pedido)
    pedido_total = 0
    pedido_itens_qt = 0

    if pedido.status != 0:
        return redirect('pedido_details', pk=pedido.pk)

    if pedido.status == 0:
        pedido.status = 1
        pedido.save()

        # TODO: Configurar função para envio do novo pedido para o Gerente
        pedido_send_mail(request, pk=pedido.pk)

    for item in pedido_itens:
        subtotal = item.quantidade * item.valor_unitario
        pedido_total = pedido_total + subtotal

    return render(request, 'pedidos/pedido_fechado.html', {'parceiro': parceiro,
                                                           'usuario': usuario,
                                                           'pedido': pedido,
                                                           'pedido_itens': pedido_itens,
                                                           'pedido_total': pedido_total,
                                                           'pedido_itens_qt': pedido_itens_qt})


@login_required
def pedido_details(request, pk):
    try:
        usuario = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        usuario = None

    parceiro = User.objects.get(username=request.user)
    pedido = Pedido.objects.get(pk=pk)

    if pedido.parceiro != parceiro:
        if parceiro.groups.filter(name='Gerente').exists() or request.user.is_superuser:
            pass
        else:
            return redirect('dashboard')

    pedido_itens = PedidoItem.objects.all().filter(pedido__exact=pedido)
    pedido_total = 0
    pedido_itens_qt = 0

    for item in pedido_itens:
        subtotal = item.quantidade * item.valor_unitario
        pedido_total = pedido_total + subtotal

    return render(request, 'pedidos/pedido_fechado.html', {'parceiro': parceiro,
                                                           'usuario': usuario,
                                                           'pedido': pedido,
                                                           'pedido_itens': pedido_itens,
                                                           'pedido_total': pedido_total,
                                                           'pedido_itens_qt': pedido_itens_qt})


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    # use short variable names
    s_url = settings.STATIC_URL  # Typically /static/
    s_root = settings.STATIC_ROOT  # Typically /home/userX/project_static/
    m_url = settings.MEDIA_URL  # Typically /static/media/
    m_root = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/

    # convert URIs to absolute system paths
    if uri.startswith(m_url):
        path = os.path.join(m_root, uri.replace(m_url, ""))
    elif uri.startswith(s_url):
        path = os.path.join(s_root, uri.replace(s_url, ""))
    else:
        return uri  # handle absolute uri (ie: http://some.tld/foo.png)

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (s_url, m_url)
        )
    return path


@login_required
def pedido_export_pdf(request, pk):
    try:
        usuario = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        usuario = None

    parceiro = User.objects.get(username=request.user)
    pedido = Pedido.objects.get(pk=pk)

    if pedido.parceiro != parceiro:
        if parceiro.groups.filter(name='Gerente').exists() or request.user.is_superuser:
            pass
        else:
            return redirect('dashboard')

    pedido_itens = PedidoItem.objects.all().filter(pedido__exact=pedido)
    pedido_total = 0
    pedido_itens_qt = 0

    for item in pedido_itens:
        subtotal = item.quantidade * item.valor_unitario
        pedido_total = pedido_total + subtotal

    ssl._create_default_https_context = ssl._create_unverified_context

    template_path = 'pedidos/pedido_pdf.html'
    context = {'parceiro': parceiro,
               'usuario': usuario,
               'pedido': pedido,
               'pedido_itens': pedido_itens,
               'pedido_total': pedido_total,
               'pedido_itens_qt': pedido_itens_qt}

    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf;charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="Pedido_{pedido.pk}.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(html, dest=response, encoding='utf8', link_callback=link_callback)
    # if error then show some funy view
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')

    return response


@login_required
def pedido_delivery_term_pdf(request, pk):
    try:
        usuario = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        usuario = None

    parceiro = User.objects.get(username=request.user)
    pedido = Pedido.objects.get(pk=pk)

    if pedido.parceiro != parceiro:
        if parceiro.groups.filter(name='Gerente').exists() or request.user.is_superuser:
            pass
        else:
            return redirect('dashboard')

    pedido_itens = PedidoItem.objects.all().filter(pedido__exact=pedido)
    pedido_total = 0
    pedido_itens_qt = 0

    for item in pedido_itens:
        subtotal = item.quantidade * item.valor_unitario
        pedido_total = pedido_total + subtotal

    ssl._create_default_https_context = ssl._create_unverified_context

    template_path = 'pedidos/pedido_delivery_term_pdf.html'
    context = {'parceiro': parceiro,
               'usuario': usuario,
               'pedido': pedido,
               'pedido_itens': pedido_itens,
               'pedido_total': pedido_total,
               'pedido_itens_qt': pedido_itens_qt}

    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf;charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="Pedido_{pedido.pk}-termo_de_entrega.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(html, dest=response, encoding='utf8', link_callback=link_callback)
    # if error then show some funy view
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')

    return response


@login_required
def pedido_delivery_term_with_order_pdf(request, pk):
    try:
        usuario = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        usuario = None

    parceiro = User.objects.get(username=request.user)
    pedido = Pedido.objects.get(pk=pk)

    if pedido.parceiro != parceiro:
        if parceiro.groups.filter(name='Gerente').exists() or request.user.is_superuser:
            pass
        else:
            return redirect('dashboard')

    pedido_itens = PedidoItem.objects.all().filter(pedido__exact=pedido)
    pedido_total = 0
    pedido_itens_qt = 0

    for item in pedido_itens:
        subtotal = item.quantidade * item.valor_unitario
        pedido_total = pedido_total + subtotal

    ssl._create_default_https_context = ssl._create_unverified_context

    template_path = 'pedidos/pedido_e_termo_pdf.html'
    context = {'parceiro': parceiro,
               'usuario': usuario,
               'pedido': pedido,
               'pedido_itens': pedido_itens,
               'pedido_total': pedido_total,
               'pedido_itens_qt': pedido_itens_qt}

    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf;charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="Pedido_e_termo_de_entrega-{pedido.pk}.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(html, dest=response, encoding='utf8', link_callback=link_callback)
    # if error then show some funy view
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')

    return response


@login_required
def pedidos_list(request):
    try:
        usuario = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        usuario = None

    parceiro = User.objects.get(username=request.user)

    if parceiro.groups.filter(name='Gerente').exists() or request.user.is_superuser:
        pedidos = Pedido.objects.all().order_by('-pk')
    else:
        pedidos = Pedido.objects.all().filter(parceiro=parceiro).order_by('-pk')

    for pedido in pedidos:
        pedido.valor_total = 0
        pedido_itens = PedidoItem.objects.all().filter(pedido__exact=pedido)
        for item in pedido_itens:
            subtotal = item.quantidade * item.valor_unitario
            pedido.valor_total = pedido.valor_total + subtotal

    parceiro = User.objects.get(username=request.user)

    pedido = Pedido.objects.filter(parceiro=parceiro, status=0).first()
    if pedido is None:
        pedido_itens_qt = 0
    else:
        pedido_itens_qt = PedidoItem.objects.filter(pedido=pedido).count()

    context = {'parceiro': parceiro,
               'usuario': usuario,
               'pedidos': pedidos,
               'pedido_itens_qt': pedido_itens_qt, }

    return render(request, 'pedidos/list.html', context)


@login_required
def pedido_send_mail(request, pk):
    pedido = Pedido.objects.get(pk=pk)
    pedido_itens = PedidoItem.objects.all().filter(pedido__exact=pedido)
    pedido_total = 0
    url = reverse('pedido_details', kwargs={'pk': pedido.pk})
    pedido_url = ''.join(['https://', get_current_site(request).domain, url])

    for item in pedido_itens:
        subtotal = item.quantidade * item.valor_unitario
        pedido_total = pedido_total + subtotal

    context = {'pedido': pedido,
               'pedido_itens': pedido_itens,
               'pedido_total': pedido_total,
               'pedido_url': pedido_url, }

    subject = 'Novo pedido de revenda'
    html_message = get_template('pedidos/pedido_mail.html').render(context)
    plain_message = strip_tags(html_message)
    from_email = config('EMAIL_HOST_USER', default='')
    to = config('PEDIDO_MAIL', default='')

    send_mail(subject, plain_message, from_email, [to], html_message=html_message)
    messages.info(request, 'O seu pedido foi enviado.')

    return redirect('pedido_details', pk=pedido.pk)
