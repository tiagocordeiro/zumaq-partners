from datetime import datetime

from django.core.management import BaseCommand

from core.facade import get_usd_cny_exchange
from core.models import CotacoesMoedas


class Command(BaseCommand):
    help = '''Atualiza cotações no banco de dados'''

    def handle(self, *args, **options):
        cotacoes_moedas = get_usd_cny_exchange()

        for cotacao in cotacoes_moedas['cotacao_cny']:
            data = datetime.strptime(cotacao["data"], "%d/%m/%Y")
            valor = cotacao["valor"]

            try:
                obj = CotacoesMoedas.objects.get(date=data)
                obj.cny = valor
                obj.save()

            except CotacoesMoedas.DoesNotExist:
                new_obj = CotacoesMoedas.objects.create(date=data, cny=valor)
                new_obj.save()

        for cotacao in cotacoes_moedas['cotacao_brl']:
            data = datetime.strptime(cotacao["data"], "%d/%m/%Y")
            valor = cotacao["valor"]

            try:
                obj = CotacoesMoedas.objects.get(date=data)
                obj.usd = valor
                obj.save()

            except CotacoesMoedas.DoesNotExist:
                new_obj = CotacoesMoedas.objects.create(date=data, usd=valor)
                new_obj.save()
