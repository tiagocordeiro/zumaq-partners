import csv
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect

from core.models import UserProfile
from pedidos.models import Pedido
from products.models import Produto


@login_required
def reports_dashboard(request):
    user = User.objects.get(username=request.user)
    if user.groups.filter(name='Gerente').exists():
        pass
    else:
        return redirect('dashboard')

    try:
        usuario = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        usuario = None

    produtos = Produto.objects.all()
    produtos_ativos = produtos.filter(active=True)
    produtos_inativos = produtos.filter(active=False)

    parceiros = User.objects.filter(groups__name__in=['Parceiro'])

    pedidos = Pedido.objects.all()
    pedidos_novos = pedidos.filter(status=1)
    pedidos_abertos = pedidos.filter(status=0)

    context = {
        'usuario': usuario,
        'produtos': produtos,
        'produtos_ativos': produtos_ativos,
        'produtos_inativos': produtos_inativos,
        'parceiros': parceiros,
        'pedidos': pedidos,
        'pedidos_novos': pedidos_novos,
        'pedidos_abertos': pedidos_abertos,
    }

    return render(request, 'reports/reports.html', context)


@login_required
def products_report(request, status='all'):
    """
    :param request:
    :param status: str
        Recebe uma string que pode ser:
        all: Todos os produtos
        ativos: Produtos ativos
        inativos: Produtos inativos
    :return:
        Retorna um csv com os produtos.
    """
    user = User.objects.get(username=request.user)
    if user.groups.filter(name='Gerente').exists():
        pass
    else:
        return redirect('dashboard')

    if status == 'ativos':
        produtos = Produto.objects.filter(active=True)
        report_name = 'ativos'
    elif status == 'inativos':
        produtos = Produto.objects.filter(active=False)
        report_name = 'inativos'
    else:
        produtos = Produto.objects.all()
        report_name = 'todos'

    report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="produtos-{report_name}-{report_date}.csv"'

    response.write(u'\ufeff'.encode('utf8'))

    writer = csv.writer(response, delimiter=';', dialect='excel')
    writer.writerow(['Descrição', 'Cliente paga - Mínimo (BRL)', 'unitário em Dolar'])
    for produto in produtos:
        writer.writerow([f'{produto.descricao}', f'{produto.cliente_paga()}', f'{produto.unitario_em_dolar()}'])

    return response


@login_required
def pedidos_report(request, status='all'):
    """
    :param request:
    :param status: str
        Recebe uma string que pode ser:
        all: Todos os pedidos
        novos: Pedidos Novos
        abertos: Pedidos em Aberto
    :return:
        Retorna um csv com os pedidos.
    """
    user = User.objects.get(username=request.user)
    if user.groups.filter(name='Gerente').exists():
        pass
    else:
        return redirect('dashboard')

    if status == 'novos':
        pedidos = Pedido.objects.filter(status=1)
        report_name = 'novos'
    elif status == 'abertos':
        pedidos = Pedido.objects.filter(active=0)
        report_name = 'abertos'
    else:
        pedidos = Pedido.objects.all()
        report_name = 'todos'

    report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="pedidos-{report_name}-{report_date}.csv"'

    response.write(u'\ufeff'.encode('utf8'))

    writer = csv.writer(response, delimiter=';', dialect='excel')
    writer.writerow(['Parceiro', 'Email parceiro', 'Data pedido', 'Status'])
    for pedido in pedidos:
        writer.writerow([f'{pedido.parceiro}',
                         f'{pedido.parceiro.email}',
                         f'{pedido.created.strftime("%d/%m/%Y")}',
                         f'{pedido.get_status_display()}'])

    return response
