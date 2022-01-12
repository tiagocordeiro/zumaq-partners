import csv
from datetime import datetime

import xlwt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.encoding import smart_str

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
    # write the headers
    writer.writerow([smart_str('Descrição'), smart_str('Cliente paga - Mínimo (BRL)'), smart_str('unitário em Dolar'),
                     smart_str('China sem imposto'), smart_str('China com imposto'), smart_str('custo da peça')])
    for produto in produtos:
        writer.writerow([smart_str(f'{produto.descricao}'),
                         smart_str(f'{round(produto.cliente_paga(), ndigits=2)}'),
                         smart_str(f'{round(produto.unitario_em_dolar(), ndigits=2)}'),
                         smart_str(f'{round(produto.ch_sem_imposto(), ndigits=2)}'),
                         smart_str(f'{round(produto.ch_com_imposto(), ndigits=2)}'),
                         smart_str(f'{round(produto.custo_da_peca(), ndigits=2)}')])

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
    # write the headers
    writer.writerow([smart_str('Parceiro'),
                     smart_str('Email parceiro'),
                     smart_str('Data pedido'),
                     smart_str('Status')])
    for pedido in pedidos:
        writer.writerow([smart_str(f'{pedido.parceiro}'),
                         smart_str(f'{pedido.parceiro.email}'),
                         smart_str(f'{pedido.created.strftime("%d/%m/%Y")}'),
                         smart_str(f'{pedido.get_status_display()}')])

    return response


@login_required
def parceiros_report(request):
    """
    :param request:
    :return:
        Retorna um csv com os parceiros.
    """
    user = User.objects.get(username=request.user)
    if user.groups.filter(name='Gerente').exists():
        pass
    else:
        return redirect('dashboard')

    parceiros = User.objects.filter(groups__name__in=['Parceiro'])
    report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="parceiros-{report_date}.csv"'

    response.write(u'\ufeff'.encode('utf8'))

    writer = csv.writer(response, delimiter=';', dialect='excel')
    # write the headers
    writer.writerow([smart_str('Parceiro'), smart_str('Email parceiro')])
    for parceiro in parceiros:
        writer.writerow([smart_str(f'{parceiro.username}'), smart_str(f'{parceiro.email}')])

    return response


@login_required()
def download_excel_products_data(request):
    # Check access role
    user = User.objects.get(username=request.user)
    if user.groups.filter(name='Gerente').exists():
        pass
    else:
        return redirect('dashboard')

    # content-type of response
    response = HttpResponse(content_type='application/ms-excel')

    # decide file name
    report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    response['Content-Disposition'] = f'attachment; filename="produtos-{report_date}.xls"'

    # creating workbook
    wb = xlwt.Workbook(encoding='utf-8')

    # adding sheet
    ws = wb.add_sheet("Produtos")

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    # headers are bold
    font_style.font.bold = True

    # column header names, you can use your own headers here
    columns = ['Código', 'Produto', 'Cliente paga - Mínimo em R$', 'Unitário em USD', 'China sem imposto',
               'China com imposto', 'Custo da Peça', 'Status']

    # write column headers in sheet
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    # get data from database.
    produtos = Produto.objects.all()

    # write sheet lines
    for produto in produtos:
        row_num = row_num + 1
        ws.write(row_num, 0, produto.codigo, font_style)
        ws.write(row_num, 1, produto.descricao, font_style)
        ws.write(row_num, 2, produto.cliente_paga(), font_style)
        ws.write(row_num, 3, produto.unitario_em_dolar(), font_style)
        ws.write(row_num, 4, produto.ch_sem_imposto(), font_style)
        ws.write(row_num, 5, produto.ch_com_imposto(), font_style)
        ws.write(row_num, 6, produto.custo_da_peca(), font_style)
        if produto.active:
            ws.write(row_num, 7, 'Ativo', font_style)
        else:
            ws.write(row_num, 7, 'Inativo', font_style)

    wb.save(response)
    return response


@login_required
def reseller_access_report(request):
    try:
        usuario = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        usuario = None

    user = User.objects.get(username=request.user)
    if user.groups.filter(name='Gerente').exists():
        pass
    else:
        return redirect('dashboard')

    parceiros = User.objects.filter(groups__name__in=['Parceiro']).order_by("-last_login")
    total_parceiros = len(parceiros)

    if total_parceiros == 1:
        total_str = f"Encontrado {total_parceiros} parceiro"
    elif total_parceiros == 0:
        total_str = "Nenhum parceiro cadastrado"
    else:
        total_str = f"Encontrados {total_parceiros} parceiros"

    return render(request, 'parceiros/access_report.html', {'usuario': usuario,
                                                            'parceiros': parceiros,
                                                            'total_parceiros': total_str, })
