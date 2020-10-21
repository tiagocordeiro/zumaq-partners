from products.models import CustomCoeficiente, CustomCoeficienteItens


def get_partner_prices(parceiro, produtos):
    partner_prices = []
    try:
        custom_coeficiente = CustomCoeficiente.objects.get(parceiro=parceiro)
        custom_prices = CustomCoeficienteItens.objects.all().filter(
            parceiro=custom_coeficiente
        )
        parceiro_coeficiente = custom_coeficiente.coeficiente_padrao

        for produto in produtos:
            try:
                c_price = custom_prices.filter(produto__codigo=produto.codigo).values(
                    "coeficiente"
                )[0]["coeficiente"]
                if c_price:
                    produto.cliente_paga = round(
                        produto.cliente_paga() + (produto.cliente_paga() * c_price),
                        ndigits=2,
                    )
                    produto.coeficiente = c_price
            except IndexError:
                produto.cliente_paga = round(
                    produto.cliente_paga()
                    + (produto.cliente_paga() * parceiro_coeficiente),
                    ndigits=2,
                )
            partner_prices.append(
                {
                    "codigo": produto.codigo,
                    "descricao": produto.descricao,
                    "estoque": produto.active,
                    "valor": produto.cliente_paga,
                }
            )

    except CustomCoeficiente.DoesNotExist:
        for produto in produtos:
            partner_prices.append(
                {
                    "codigo": produto.codigo,
                    "descricao": produto.descricao,
                    "estoque": produto.active,
                    "valor": produto.cliente_paga(),
                }
            )

    return partner_prices
