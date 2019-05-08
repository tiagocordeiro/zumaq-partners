from decimal import Decimal

from django.db import models

from core.models import Active, TimeStampedModel
from core.models import User


class Produto(TimeStampedModel, Active):
    codigo = models.CharField('Código do produto', max_length=60, primary_key=True)
    descricao = models.CharField('Descrição do produto', max_length=120)
    pago_na_china = models.DecimalField('Preço de custo em ¥', max_digits=16, decimal_places=10)
    reminmbi = models.DecimalField('Reminmbi ¥', max_digits=16, decimal_places=10)
    dolar_cotado = models.DecimalField('Em reais (R$)', max_digits=16, decimal_places=10)
    impostos_na_china = models.DecimalField('Impostos na China (%)', max_digits=10, decimal_places=2)
    porcentagem_importacao = models.DecimalField('Porcentagem Importação (%)', max_digits=10, decimal_places=2)
    coeficiente = models.DecimalField('Coeficidente (%)', max_digits=10, decimal_places=2)
    imagem = models.URLField(blank=True, null=True, default='https://via.placeholder.com/150')

    def compra_do_cambio(self):
        return round(self.dolar_cotado + Decimal('0.20'), ndigits=2)

    def ch_sem_imposto(self):
        return round(self.pago_na_china / self.reminmbi * self.compra_do_cambio(), ndigits=2)

    def ch_com_imposto(self):
        return round(self.ch_sem_imposto() * self.impostos_na_china + self.ch_sem_imposto(), ndigits=2)

    def custo_da_peca(self):
        return round(self.ch_com_imposto() * self.porcentagem_importacao + self.ch_com_imposto(), ndigits=2)

    def cliente_paga(self):
        return round(self.custo_da_peca() * self.coeficiente + self.custo_da_peca(), ndigits=2)

    def unitario_em_dolar(self):
        return round(self.cliente_paga() / self.dolar_cotado, ndigits=2)

    def __str__(self):
        return str(self.codigo + ' - ' + self.descricao)

    class Meta:
        ordering = ('codigo', 'descricao')
        verbose_name_plural = "produtos"
        verbose_name = "produto"


class CustomCoeficiente(models.Model):
    parceiro = models.OneToOneField(User, null=True, on_delete=models.SET_NULL)
    coeficiente_padrao = models.DecimalField('Coeficidente padrão (%)',
                                             max_digits=10,
                                             decimal_places=2,
                                             default=.50)


class CustomCoeficienteItens(models.Model):
    parceiro = models.ForeignKey(CustomCoeficiente, null=True, on_delete=models.SET_NULL)
    produto = models.ForeignKey(Produto, null=True, on_delete=models.SET_NULL)
    coeficiente = models.DecimalField('Coeficidente (%)', max_digits=10, decimal_places=2)
