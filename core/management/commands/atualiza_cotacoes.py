from django.core.management import BaseCommand

from core.facade import cotacoes
from core.models import CotacoesMoedas


class Command(BaseCommand):
    help = '''Atualiza cotações no banco de dados'''

    def handle(self, *args, **options):
        cotacoes_moedas = cotacoes()
        cotacoes_moedas = cotacoes_moedas['df']
        cotacoes_moedas.columns = ['date', 'cny', 'usd']
        cotacoes_dict = []
        for cotacao in cotacoes_moedas.itertuples():
            cotacao = CotacoesMoedas(date=cotacao[1],
                                     cny=cotacao[2],
                                     usd=cotacao[3])
            cotacoes_dict.append(cotacao)

        last_in_dict = cotacoes_dict[-1].date
        try:
            last_in_db = CotacoesMoedas.objects.last().date
            if last_in_db < last_in_dict:
                print(f"No banco: {last_in_db}, mais recente: {last_in_dict}")
                CotacoesMoedas.objects.all().delete()
                CotacoesMoedas.objects.bulk_create(cotacoes_dict)
                print("Cotações atualizadas")

        except AttributeError:
            print(f"No banco: vazio, mais recente: {last_in_dict}")
            CotacoesMoedas.objects.bulk_create(cotacoes_dict)
            print("Cotações adicionadas")
