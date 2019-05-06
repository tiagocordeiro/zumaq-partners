import csv
from django.http import HttpResponse
from products.models import Produto

def products_report(request):
    # Create the HttpResponse object with the appropriate CSV header.
    produtos = Produto.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="produtos.csv"'

    writer = csv.writer(response)
    writer.writerow(['Descrição', 'Cliente paga - Mínimo (BRL)', 'unitário em Dolar'])
    for produto in produtos:
        writer.writerow([f'{produto.descricao}', f'{produto.cliente_paga()}', f'{produto.unitario_em_dolar()}'])

    return response
