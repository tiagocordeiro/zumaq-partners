from decimal import Decimal

from django.test import TestCase

from .models import Produto


class AnimalTestCase(TestCase):
    def setUp(self):
        Produto.objects.create(codigo='TYL-1080',
                               descricao='Tubo de Laser Yong Li - 80w - R3',
                               pago_na_china=880,
                               reminmbi=6.84,
                               dolar_cotado=3.89,
                               compra_do_cambio=4.09,
                               impostos_na_china=0,
                               porcentagem_importacao=0.52,
                               coeficiente=0.50)

    def test_retorno_ch_sem_imposto(self):
        produto = Produto.objects.get(codigo='TYL-1080')
        self.assertEqual(produto.ch_sem_imposto(), Decimal('526.20'))

    def test_retorno_ch_com_imposto(self):
        produto = Produto.objects.get(codigo='TYL-1080')
        self.assertEqual(produto.ch_com_imposto(), Decimal('526.20'))
