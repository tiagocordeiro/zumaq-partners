from datetime import date, timedelta, datetime

import requests
from decouple import config

from core.models import CotacoesMoedas


def datetime_string_parser(value):
    """Ajusta string no formato %d/%m/%Y"""
    formated_date = value.split("-")

    return f"{formated_date[2]}/{formated_date[1]}/{formated_date[0]}"


def timestamp_string_parse(value):
    """Converte timestamp string no formato %d/%m/%Y"""
    return datetime.fromtimestamp(int(value)).strftime('%d/%m/%Y')


def get_usd_cny_exchange(start_date=None, end_date=None):
    """Inserir data no formato mm-dd-yyyy"""

    hoje = date.today()
    inicio_periodo = hoje - timedelta(weeks=4)

    if start_date is None:
        start_date = inicio_periodo.strftime('%m-%d-%Y')

    if end_date is None:
        end_date = hoje.strftime("%m-%d-%Y")

    cotacao_cny = []
    cotacao_brl = []

    url = 'https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/'
    url += 'CotacaoDolarPeriodo(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)'
    url += f'?@dataInicial=%27{start_date}%27&@dataFinalCotacao=%27{end_date}%27&$top=1000&$format=json'

    response = requests.get(url)
    result = response.json().get('value')
    if result:
        '''
        Gera uma list comprehension convertendo o datetime em date
        e gerando um tupla com data e cotacaoVenda.
        Ex:
        [
            ('2021-07-01', 5.0055),
            ('2021-07-02', 5.0293),
            ('2021-07-05', 5.0749)
        ]
        '''
        data_indexed = [
            (item['dataHoraCotacao'].split()[0], item['cotacaoVenda']) for item in result
        ]

        for cotacao in data_indexed:
            cotacao_brl.append({'data': datetime_string_parser(cotacao[0]), 'valor': round(cotacao[1], ndigits=2)})

    cny_url = "https://awesomeapi-exchange.p.rapidapi.com/json/list/USD-CNY/30"

    x_rapidapi_key = config('X_RAPIDAPI_KEY')
    x_rapidapi_host = config('X_RAPIDAPI_HOST')

    headers = {
        'x-rapidapi-key': x_rapidapi_key,
        'x-rapidapi-host': x_rapidapi_host
    }

    response_cny = requests.request("GET", cny_url, headers=headers)
    result_cny = response_cny.json()
    if result_cny:
        data_indexed_cny = [
            (item['timestamp'], item['ask']) for item in result_cny
        ]

        data_indexed_cny.reverse()

        for cotacao in data_indexed_cny:
            cotacao_cny.append({'data': timestamp_string_parse(cotacao[0]), 'valor': cotacao[1]})

    return {'cotacao_cny': cotacao_cny, 'cotacao_brl': cotacao_brl}


def cotacoes():
    cotacoes_cny_from_db = CotacoesMoedas.objects.filter(cny__isnull=False).order_by('-date')[:30]
    cotacoes_usd_from_db = CotacoesMoedas.objects.filter(usd__isnull=False).order_by('-date')[:30]

    cotacao_cny = []
    cotacao_brl = []

    for cotacao in cotacoes_cny_from_db:
        cotacao_cny.append({'data': cotacao.date.strftime('%d/%m/%Y'),
                            'valor': str(cotacao.cny)})

    for cotacao in cotacoes_usd_from_db:
        cotacao_brl.append({'data': cotacao.date.strftime('%d/%m/%Y'),
                            'valor': str(cotacao.usd)})

    return {'cotacao_cny': cotacao_cny[::-1], 'cotacao_brl': cotacao_brl[::-1]}
