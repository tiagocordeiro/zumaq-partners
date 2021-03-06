from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.forms.models import inlineformset_factory
from django.shortcuts import render, redirect

from pedidos.models import Pedido, PedidoItem
from products.forms import CustomCoeficienteForm, CustomCoeficienteItensForm, BlockedProductsForm, CustomBlockedForm
from products.models import CustomCoeficiente, CustomCoeficienteItens, Produto, BlockedProducts, CustomBlocked
from .facade import cotacoes
from .forms import ProfileForm, CadastroParceiro
from .models import UserProfile


@login_required
def dashboard(request):
    cotacoes_moedas = cotacoes()
    cotacao_cny = cotacoes_moedas['cotacao_cny']
    cotacao_brl = cotacoes_moedas['cotacao_brl']

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

    user = User.objects.get(username=request.user)

    produtos_qt = Produto.objects.all().filter(active=True).count()

    if parceiro.groups.filter(name='Parceiro'):
        pedidos_itens = PedidoItem.objects.all().filter(pedido__status__gte=1, pedido__parceiro=parceiro)
    else:
        pedidos_itens = PedidoItem.objects.all().filter(pedido__status__gte=1)

    pedidos_valor_total = 0
    for item in pedidos_itens:
        subtotal = item.quantidade * item.valor_unitario
        pedidos_valor_total = pedidos_valor_total + subtotal

    pedidos_qt_all = Pedido.objects.all().filter(status__gte=1).count()
    pedidos_qt_parceiro = Pedido.objects.all().filter(status__gte=1, parceiro=parceiro).count()

    context = {'produtos_qt': produtos_qt,
               'usuario': usuario,
               'user': user,
               'cotacao_cny': cotacao_cny,
               'cotacao_brl': cotacao_brl,
               'pedido_itens_qt': pedido_itens_qt,
               'pedidos_qt_all': pedidos_qt_all,
               'pedidos_qt_parceiro': pedidos_qt_parceiro,
               'pedidos_valor_total': pedidos_valor_total,
               }

    return render(request, 'dashboard_demo.html', context)


@login_required
def profile_update(request):
    try:
        usuario = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        usuario = None

    user = User.objects.get(username=request.user)

    ProfileInlineFormset = inlineformset_factory(User, UserProfile, fields=('avatar',))

    if request.method == 'POST':
        form = ProfileForm(data=request.POST, instance=request.user)
        formset = ProfileInlineFormset(request.POST, request.FILES, instance=request.user)

        if form.is_valid():
            perfil = form.save(commit=False)
            formset = ProfileInlineFormset(request.POST, request.FILES, instance=perfil)

            if formset.is_valid():
                perfil.save()
                formset.save()
                return redirect('dashboard')

    else:
        form = ProfileForm(instance=request.user)
        formset = ProfileInlineFormset(instance=request.user)

    return render(request, 'profile_update.html', {'form': form,
                                                   'formset': formset,
                                                   'usuario': usuario,
                                                   'user': user, })


@login_required
def parceiro_cadastro(request):
    if request.method == 'POST':
        form = CadastroParceiro(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            user = User.objects.get(username=username)
            group = Group.objects.get(name="Parceiro")
            user.groups.add(group)
            return redirect('parceiro_list')
    else:
        form = CadastroParceiro()
    return render(request, 'registration/cadastro_parceiro.html', {'form': form})


@login_required
def parceiro_list(request):
    try:
        usuario = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        usuario = None

    user = User.objects.get(username=request.user)
    if user.groups.filter(name='Gerente').exists():
        pass
    else:
        return redirect('dashboard')

    parceiros = User.objects.filter(groups__name__in=['Parceiro'])
    total_parceiros = len(parceiros)

    if total_parceiros == 1:
        total_str = f"Encontrado {total_parceiros} parceiro"
    elif total_parceiros == 0:
        total_str = "Nenhum parceiro cadastrado"
    else:
        total_str = f"Encontrados {total_parceiros} parceiros"

    return render(request, 'parceiros/list.html', {'usuario': usuario,
                                                   'parceiros': parceiros,
                                                   'total_parceiros': total_str, })


@login_required
def parceiro_create(request):
    try:
        usuario = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        usuario = None

    user = User.objects.get(username=request.user)
    if user.groups.filter(name='Gerente').exists():
        if request.method == 'POST':
            form = CadastroParceiro(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                user = User.objects.get(username=username)
                group = Group.objects.get(name="Parceiro")
                user.groups.add(group)
                return redirect('parceiro_list')
        else:
            form = CadastroParceiro()
        return render(request, 'parceiros/create.html', {'form': form,
                                                         'usuario': usuario})
    else:
        return redirect('dashboard')


@login_required
def parceiro_details(request, pk):
    # Check access role
    user = User.objects.get(username=request.user)
    if user.groups.filter(name='Gerente').exists():
        pass
    else:
        return redirect('dashboard')

    try:
        usuario = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        usuario = None

    parceiro = User.objects.get(pk=pk)

    try:
        parceiro_coeficientes = CustomCoeficiente.objects.get(parceiro=parceiro)
    except CustomCoeficiente.DoesNotExist:
        parceiro_coeficientes = CustomCoeficiente.objects.create(parceiro=parceiro)

    custom_prices = CustomCoeficienteItens.objects.all().filter(parceiro=parceiro_coeficientes)

    custom_itens_formset = inlineformset_factory(
        CustomCoeficiente, CustomCoeficienteItens, form=CustomCoeficienteItensForm, extra=0, can_delete=True)

    if request.method == 'POST':
        form = CustomCoeficienteForm(request.POST, instance=parceiro_coeficientes, prefix='main')
        formset = custom_itens_formset(request.POST, instance=parceiro_coeficientes, prefix='product')

        try:
            if formset.is_valid() and form.is_valid():
                form.save()
                formset.save()
                messages.success(request, "Coeficientes atualizados.")
                return redirect(parceiro_details, pk=parceiro.pk)

        except Exception as e:
            messages.warning(request, 'Ocorreu um erro ao atualizar: {}'.format(e))

    else:
        form = CustomCoeficienteForm(instance=parceiro_coeficientes, prefix='main')
        formset = custom_itens_formset(instance=parceiro_coeficientes, prefix='product')

    context = {
        'custom_prices': custom_prices,
        'parceiro_coeficientes': parceiro_coeficientes,
        'form': form,
        'formset': formset,
        'usuario': usuario,
        'parceiro': parceiro,
    }

    return render(request, 'parceiros/details.html', context)


@login_required
def parceiro_blocked_details(request, pk):
    # Check access role
    user = User.objects.get(username=request.user)
    if user.groups.filter(name='Gerente').exists():
        pass
    else:
        return redirect('dashboard')

    try:
        usuario = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        usuario = None

    parceiro = User.objects.get(pk=pk)

    try:
        parceiro_blocked_items = CustomBlocked.objects.get(parceiro=parceiro)
    except CustomBlocked.DoesNotExist:
        parceiro_blocked_items = CustomBlocked.objects.create(parceiro=parceiro)

    custom_blocked = BlockedProducts.objects.all().filter(parceiro=parceiro_blocked_items)

    custom_itens_formset = inlineformset_factory(
        CustomBlocked, BlockedProducts, form=BlockedProductsForm, extra=0, can_delete=True)

    if request.method == 'POST':
        form = CustomBlockedForm(request.POST, instance=parceiro_blocked_items, prefix='main')
        formset = custom_itens_formset(request.POST, instance=parceiro_blocked_items, prefix='product')

        try:
            if formset.is_valid() and form.is_valid():
                form.save()
                formset.save()
                messages.success(request, "Produtos restritos atualizados.")
                return redirect(parceiro_blocked_details, pk=parceiro.pk)

        except Exception as e:
            messages.warning(request, 'Ocorreu um erro ao atualizar: {}'.format(e))

    else:
        form = CustomBlockedForm(instance=parceiro_blocked_items, prefix='main')
        formset = custom_itens_formset(instance=parceiro_blocked_items, prefix='product')

    context = {
        'custom_blocked': custom_blocked,
        'parceiro_blocked_items': parceiro_blocked_items,
        'form': form,
        'formset': formset,
        'usuario': usuario,
        'parceiro': parceiro,
    }

    return render(request, 'parceiros/blocked.html', context)
