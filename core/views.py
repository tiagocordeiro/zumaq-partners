import os
from datetime import date, timedelta

import pandas as pd
import quandl
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.forms.models import inlineformset_factory
from django.shortcuts import render, redirect

from products.forms import CustomCoeficienteForm, CustomCoeficienteItensForm
from products.models import CustomCoeficiente, CustomCoeficienteItens, Produto
from .forms import ProfileForm, CadastroParceiro
from .models import UserProfile


@login_required
def dashboard(request):
    quandl.ApiConfig.api_key = os.environ.get('QUANDL_KEY')
    hoje = date.today()
    periodo = hoje - timedelta(weeks=4)
    cotacao_moedas = quandl.get(["BUNDESBANK/BBEX3_D_CNY_USD_CA_AC_000",
                                 "BUNDESBANK/BBEX3_D_BRL_USD_CA_AB_000"],
                                start_date=periodo.isoformat(), returns="pandas")

    df = pd.DataFrame(cotacao_moedas)
    df.reset_index(level=0, inplace=True)

    df.fillna(method='ffill', inplace=True)
    df.fillna(method='bfill', inplace=True)

    cotacao_cny = []
    cotacao_brl = []
    cny_spark = []

    for cotacao in df.values:
        cotacao_cny.append({'data': cotacao[0].strftime('%d/%m/%Y'), 'valor': round(cotacao[1], ndigits=2)})
        cotacao_brl.append({'data': cotacao[0].strftime('%d/%m/%Y'), 'valor': round(cotacao[2], ndigits=2)})
        cny_spark.append(round(cotacao[1], ndigits=2))

    cny_spark_str = str(cny_spark).strip('[]')

    try:
        usuario = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        usuario = None

    user = User.objects.get(username=request.user)

    produtos_qt = Produto.objects.all().count()

    context = {'produtos_qt': produtos_qt,
               'usuario': usuario,
               'user': user,
               'cotacao_cny': cotacao_cny,
               'cotacao_brl': cotacao_brl,
               'cny_spark': cny_spark,
               'cny_spark_str': cny_spark_str,
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
        total_str = f"Nenhum parceiro cadastrado"
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
            if formset.is_valid():
                # form.save()
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

    # return render(request, 'notas/edit.html', context)

    return render(request, 'parceiros/details.html', context)
