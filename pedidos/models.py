from django.contrib.auth.models import User
from django.db import models

from core.models import Active, TimeStampedModel
from products.models import Produto


class Pedido(TimeStampedModel, Active):
    STATUS_CHOICES = (
        (0, 'Aberto'),
        (1, 'Enviado'),
        (2, 'Finalizado'),
        (3, 'Cancelado'),
    )
    parceiro = models.ForeignKey(User, verbose_name='parceiro', on_delete=models.CASCADE)
    status = models.IntegerField('Situação', choices=STATUS_CHOICES, default=0, blank=True)
    observacoes = models.TextField('Observações', blank=True, null=True)

    def __str__(self):
        return str(self.pk) + ' - ' + str(self.parceiro.username)

    class Meta:
        verbose_name = 'pedido'
        verbose_name_plural = 'pedidos'


class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    item = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField('Quantidade', default=1)
    valor_unitario = models.DecimalField('Valor Un.', max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return str(self.item.descricao)

    class Meta:
        verbose_name = 'item'
        verbose_name_plural = 'itens'
