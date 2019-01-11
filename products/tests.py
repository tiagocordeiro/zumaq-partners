from decimal import Decimal

from django.contrib.auth.models import User, Group, AnonymousUser
from django.test import TestCase, RequestFactory, Client
from django.urls import reverse

from .models import Produto
from .views import product_add, product_update


class ProductsTestCase(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.client = Client()
        self.user_gerente = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')
        self.group = Group.objects.create(name='Gerente')
        self.group.user_set.add(self.user_gerente)

        self.product = Produto.objects.create(codigo='TYL-1080',
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

    def test_product_add_anonimo(self):
        request = self.factory.get(reverse('product_add'))
        request.user = AnonymousUser()

        response = product_add(request)
        self.assertEqual(response.status_code, 302)
        # request = self.factory.get(reverse('product_add'))
        # self.client.force_login(self.user_gerente)
        # request.user = AnonymousUser()

        # response = product_add(request)
        # response = self.client.get(reverse('product_add'))
        # self.assertEqual(response.status_code, 302)
        # self.assertRedirects(response, '/accounts/login/?next=/products/product/add/')

    def test_product_add_gerente(self):
        request = self.factory.get(reverse('product_add'))
        request.user = self.user_gerente

        response = product_add(request)
        self.assertEqual(response.status_code, 200)
        # self.client.force_login(self.user_gerente)
        # response = self.client.get(reverse('product_add'))
        # self.assertEqual(response.status_code, 200)

    def test_product_update(self):
        produto = self.product

        # self.client.force_login(self.user_gerente)

        form_data = {'codigo': 'TYL-1080',
                     'descricao': 'Tubo de Laser Yong Li - 80w - R3',
                     'pago_na_china': 880,
                     'reminmbi': 6.84,
                     'dolar_cotado': 3.89,
                     'impostos_na_china': 0,
                     'porcentagem_importacao': 0.52,
                     'coeficiente': 0.11, }

        request = self.factory.post(reverse('product_update', kwargs={'codigo': produto.codigo}), form_data)
        request.user = self.user_gerente

        response = product_update(request, codigo=produto.codigo)
        # response = self.factory.post(reverse('product_update', kwargs={'codigo': produto.codigo}), form_data)

        produto.refresh_from_db()
        self.assertEqual(produto.coeficiente, Decimal('0.11'))
        self.assertEqual(response.status_code, 302)

    def test_product_create_exist_status_code_gerente(self):
        self.client.force_login(self.user_gerente)
        response = self.client.post(reverse('product_create', kwargs={'codigo': self.product.codigo}))
        print(response)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/products/product/update/TYL-1080/', status_code=302, target_status_code=200)
