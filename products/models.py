from django.db import models
from decimal import Decimal


class Produto(models.Model):
    codigo = models.CharField('Código do produto', max_length=60, primary_key=True)
    descricao = models.CharField('Descrição do produto', max_length=120)
    pago_na_china = models.DecimalField('Preço de custo em ¥', max_digits=16, decimal_places=10)
    reminmbi = models.DecimalField('Reminmbi ¥', max_digits=16, decimal_places=10)
    dolar_cotado = models.DecimalField('Em reais (R$)', max_digits=16, decimal_places=10)
    impostos_na_china = models.DecimalField('Impostos na China (%)', max_digits=10, decimal_places=2)
    porcentagem_importacao = models.DecimalField('Porcentagem Importação (%)', max_digits=10, decimal_places=2)
    coeficiente = models.DecimalField('Coeficidente (%)', max_digits=10, decimal_places=2)

    def compra_do_cambio(self):
        return round(self.dolar_cotado + Decimal('0.20'), ndigits=2)

    def ch_sem_imposto(self):
        return round(self.pago_na_china / self.reminmbi * self.compra_do_cambio(), ndigits=2)

    def ch_com_imposto(self):
        return round(self.ch_sem_imposto() * self.impostos_na_china + self.ch_sem_imposto(), ndigits=2)

    class Meta:
        verbose_name_plural = "produtos"
        verbose_name = "produto"
