from django.db import models


class Produto(models.Model):
    codigo = models.CharField('Código do produto', max_length=60, primary_key=True)
    descricao = models.CharField('Descrição do produto', max_length=120)
    pago_na_china = models.DecimalField('Preço de custo em ¥', max_digits=16, decimal_places=10)
    reminmbi = models.DecimalField('Reminmbi ¥', max_digits=16, decimal_places=10)
    dolar_cotado = models.DecimalField('Em reais (R$)', max_digits=16, decimal_places=10)
    compra_do_cambio = models.DecimalField('Em reais (R$)', max_digits=16, decimal_places=10)
    impostos_na_china = models.DecimalField('Impostos na China (%)', max_digits=10, decimal_places=2)
    porcentagem_importacao = models.DecimalField('Porcentagem Importação (%)', max_digits=10, decimal_places=2)
    coeficiente = models.DecimalField('Coeficidente (%)', max_digits=10, decimal_places=2)

    def ch_sem_imposto(self):
        return self.pago_na_china / self.reminmbi * self.compra_do_cambio

    class Meta:
        verbose_name_plural = "produtos"
        verbose_name = "produto"
