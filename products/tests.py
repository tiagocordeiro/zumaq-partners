from decimal import Decimal

from django.test import TestCase

from .models import Produto


class ProductsTestCase(TestCase):
    def setUp(self):
        Produto.objects.create(codigo='TYL-1080',
                               descricao='Tubo de Laser Yong Li - 80w - R3',
                               pago_na_china=880,
                               reminmbi=6.84,
                               dolar_cotado=3.89,
                               impostos_na_china=0,
                               porcentagem_importacao=0.52,
                               coeficiente=0.50)

    def test_retorno_ch_sem_imposto(self):
        produto = Produto.objects.get(codigo='TYL-1080')
        self.assertEqual(produto.ch_sem_imposto(), Decimal('526.20'))

    def test_retorno_ch_com_imposto(self):
        produto = Produto.objects.get(codigo='TYL-1080')
        self.assertEqual(produto.ch_com_imposto(), Decimal('526.20'))

    def test_retorno_compra_do_cambio(self):
        produto = Produto.objects.get(codigo='TYL-1080')
        self.assertEqual(produto.compra_do_cambio(), Decimal('4.09'))

    def test_retorno_custo_da_peca(self):
        produto = Produto.objects.get(codigo='TYL-1080')
        self.assertEqual(produto.custo_da_peca(), Decimal('799.82'))

    def test_retorno_cliente_paga(self):
        produto = Produto.objects.get(codigo='TYL-1080')
        self.assertEqual(produto.cliente_paga(), Decimal('1199.73'))

    def test_retorno_valor_unitario_em_dolar(self):
        produto = Produto.objects.get(codigo='TYL-1080')
        self.assertEqual(produto.unitario_em_dolar(), Decimal('308.41'))
