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
    status = models.IntegerField(
        'Situação', choices=STATUS_CHOICES, default=0, blank=True
    )

    class Meta:
        verbose_name = 'pedido'
        verbose_name_plural = 'pedidos'


class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, null=True, on_delete=models.SET_NULL)
    item = models.ForeignKey(Produto, null=True, on_delete=models.SET_NULL)
    quantidade = models.PositiveIntegerField('Quantidade', default=1)
    valor_unitario = models.DecimalField('Valor Un.', max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = 'item'
        verbose_name_plural = 'itens'
