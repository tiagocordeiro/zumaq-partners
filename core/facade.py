import os
from datetime import date, timedelta

import pandas as pd
import quandl


def cotacoes():
    quandl.ApiConfig.api_key = os.environ.get('QUANDL_KEY')
    hoje = date.today()
    periodo = hoje - timedelta(weeks=4)
    cotacao_moedas = quandl.get(["BUNDESBANK/BBEX3_D_CNY_USD_CA_AC_000",
                                 "BUNDESBANK/BBEX3_D_BRL_USD_CA_AB_000"],
                                start_date=periodo.isoformat(),
                                returns="pandas")

    df = pd.DataFrame(cotacao_moedas)
    df.reset_index(level=0, inplace=True)

    df.fillna(method='ffill', inplace=True)
    df.fillna(method='bfill', inplace=True)

    cotacao_cny = []
    cotacao_brl = []

    for cotacao in df.values:
        cotacao_cny.append({'data': cotacao[0].strftime('%d/%m/%Y'),
                            'valor': round(cotacao[1], ndigits=2)})
        cotacao_brl.append({'data': cotacao[0].strftime('%d/%m/%Y'),
                            'valor': round(cotacao[2], ndigits=2)})

    return {'cotacao_cny': cotacao_cny, 'cotacao_brl': cotacao_brl, 'df': df}
