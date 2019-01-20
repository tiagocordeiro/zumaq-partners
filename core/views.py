from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.forms.models import inlineformset_factory
from django.shortcuts import render, redirect

from .forms import ProfileForm, CadastroParceiro
from .models import UserProfile


@login_required
def dashboard(request):
    try:
        usuario = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        usuario = None

    user = User.objects.get(username=request.user)

    return render(request, 'dashboard_demo.html', {'usuario': usuario,
                                                   'user': user, })


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
