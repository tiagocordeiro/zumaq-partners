import json
import os
from decimal import Decimal

import responses
from django.contrib.auth.models import User, Group
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import TestCase, RequestFactory, Client
from django.urls import reverse

from products.models import Produto, CustomCoeficiente, CustomCoeficienteItens, ProdutoAtacado
from products.views import product_add, product_update


class ProductsTestCase(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.client = Client()

        # User Gerente
        self.user_gerente = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')
        self.group_gerente = Group.objects.create(name='Gerente')
        self.group_gerente.user_set.add(self.user_gerente)

        # User Parceiro
        self.user_parceiro = User.objects.create_user(username='joe', email='joe@…', password='top_secret')
        self.group_parceiro = Group.objects.create(name='Parceiro')
        self.group_parceiro.user_set.add(self.user_parceiro)

        # User Parceiro 2
        self.user_parceiro2 = User.objects.create_user(username='james', email='james@foo.bar', password='secret')
        self.group_parceiro.user_set.add(self.user_parceiro2)

        # Produto
        self.product = Produto.objects.create(codigo='TYL-1080',
                                              descricao='Tubo de Laser Yong Li - 80w - R3',
                                              pago_na_china=880,
                                              reminmbi=6.84,
                                              dolar_cotado=3.89,
                                              impostos_na_china=0,
                                              porcentagem_importacao=0.52,
                                              coeficiente=0.50)

        self.product_atacado = ProdutoAtacado.objects.create(produto=self.product, quantidade=6, coeficiente=0.45)

        # Custom coeficiente de parceiro
        self.parceiro_coeficiente = CustomCoeficiente.objects.create(parceiro=self.user_parceiro,
                                                                     coeficiente_padrao=0.48)

        # Custom coeficiente de parceiro / produto
        self.parceiro_product_coeficiente = CustomCoeficienteItens.objects.create(parceiro=self.parceiro_coeficiente,
                                                                                  produto=self.product,
                                                                                  coeficiente=0.45)

        # Custom coeficiente de parceiro2
        # O coeficiente padrão deve ser .50
        self.parceiro2_coefiente = CustomCoeficiente.objects.create(parceiro=self.user_parceiro2)

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
        self.client.logout()
        response = self.client.get(reverse('product_add'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/products/product/add/',
                             status_code=302, target_status_code=200)

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
                     'main-pago_na_china': 880,
                     'main-reminmbi': 6.84,
                     'main-dolar_cotado': 3.89,
                     'main-impostos_na_china': 0,
                     'main-porcentagem_importacao': 0.52,
                     'main-coeficiente': 0.49,
                     'product-TOTAL_FORMS': 0,
                     'product-INITIAL_FORMS': 0,
                     'product-MIN_NUM_FORMS': 0,
                     'product-MAX_NUM_FORMS': 1000,
                     }

        request = self.factory.post(reverse('product_update', kwargs={'codigo': produto.codigo}), form_data)
        request.user = self.user_gerente
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = product_update(request, codigo=produto.codigo)

        produto.refresh_from_db()
        self.assertEqual(produto.coeficiente, Decimal('0.49'))
        self.assertEqual(response.status_code, 302)

    def test_product_atacado_update(self):
        produto = self.product
        produto_atacado = self.product_atacado

        # self.client.force_login(self.user_gerente)

        form_data = {'codigo': 'TYL-1080',
                     'descricao': 'Tubo de Laser Yong Li - 80w - R3',
                     'main-pago_na_china': 880,
                     'main-reminmbi': 6.84,
                     'main-dolar_cotado': 3.89,
                     'main-impostos_na_china': 0,
                     'main-porcentagem_importacao': 0.52,
                     'main-coeficiente': 0.49,
                     'product-TOTAL_FORMS': 1,
                     'product-INITIAL_FORMS': 1,
                     'product-MIN_NUM_FORMS': 0,
                     'product-MAX_NUM_FORMS': 1000,
                     'product-0-id': self.product_atacado.pk,
                     'product-0-produto': self.product.pk,
                     'product-0-quantidade': 6,
                     'product-0-coeficiente': 0.44,
                     }

        request = self.factory.post(reverse('product_update', kwargs={'codigo': produto.codigo}), form_data)
        request.user = self.user_gerente

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = product_update(request, codigo=produto.codigo)

        produto.refresh_from_db()
        self.assertEqual(produto.coeficiente, Decimal('0.49'))
        produto_atacado.refresh_from_db()
        self.assertEqual(produto_atacado.coeficiente, Decimal('0.44'))
        self.assertEqual(response.status_code, 302)

    def test_product_create_exist_status_code_gerente(self):
        self.client.force_login(self.user_gerente)
        response = self.client.post(reverse('product_create', kwargs={'codigo': self.product.codigo}))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/products/product/update/TYL-1080/', status_code=302, target_status_code=200)

    def test_product_update_does_not_exist(self):
        self.client.force_login(self.user_gerente)
        response = self.client.post(reverse('product_update', kwargs={'codigo': 'AAA'}))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/products/product/create/AAA/', status_code=302, target_status_code=302)

    def test_product_list_view_anonimo(self):
        self.client.logout()
        response = self.client.get(reverse('product_list'))

        # response = product_list(request)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/products/list/',
                             status_code=302, target_status_code=200)

    def test_product_atacado_list_view_anonimo(self):
        self.client.logout()
        response = self.client.get(reverse('product_list_atacado'))

        # response = product_list(request)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/products/list/atacado/',
                             status_code=302, target_status_code=200)

    def test_product_list_view_gerente(self):
        self.client.force_login(self.user_gerente)
        response = self.client.get(reverse('product_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TYL-1080')
        self.assertContains(response, 'R$ 1.199,73')

    def test_product_atacado_list_view_gerente(self):
        self.client.force_login(self.user_gerente)
        response = self.client.get(reverse('product_list_atacado'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TYL-1080')
        self.assertContains(response, 'R$ 1.159,74')

    def test_product_list_view_parceiro(self):
        self.client.force_login(self.user_parceiro)
        response = self.client.get(reverse('product_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TYL-1080')
        self.assertContains(response, 'R$ 1.739,61')

    def test_product_atacado_list_view_parceiro(self):
        self.client.force_login(self.user_parceiro)
        response = self.client.get(reverse('product_list_atacado'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TYL-1080')
        self.assertContains(response, 'R$ 1.159,74')

    def test_product_parceiro_custom_coeficiente(self):
        self.client.force_login(self.user_parceiro)
        response = self.client.get(reverse('product_list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.parceiro_coeficiente.coeficiente_padrao, 0.48)
        self.assertEqual(self.parceiro_product_coeficiente.coeficiente, 0.45)

    def test_product_list_view_parceiro_custom_price_in_template(self):
        self.client.force_login(self.user_parceiro)
        response = self.client.get(reverse('product_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'R$ 1.739,61')

    def test_product_list_view_parceiro_product_is_promo(self):
        self.client.force_login(self.user_parceiro)
        response = self.client.get(reverse('product_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<span class="label label-red">Promoção</span>')

    def test_product_list_view_parceiro2_product_is_not_promo(self):
        self.client.force_login(self.user_parceiro2)
        response = self.client.get(reverse('product_list'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<span class="label label-red">Promoção</span>')

    def test_product_list_view_parceiro_without_custom_product_coeficiente(self):
        self.client.force_login(self.user_parceiro2)
        response = self.client.get(reverse('product_list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.parceiro2_coefiente.coeficiente_padrao, 0.50)
        self.assertContains(response, 'R$ 1.799,60')
        self.assertEqual(response.context['produtos'][0].cliente_paga, Decimal('1799.60'))

    def test_product_view_gerente(self):
        self.client.force_login(self.user_gerente)
        response = self.client.get(reverse('product_view', kwargs={'codigo': self.product.codigo}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TYL-1080')

    @responses.activate
    def test_product_create(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(dir_path + '/tyl-1100-mock.json') as json_data_file:
            data = json.load(json_data_file)

        responses.add(responses.GET, 'https://bling.com.br/Api/v2/produto/TYL-1100/json/', json=data, status=200)
        form_data = {'codigo': 'TYL-1100',
                     'descricao': 'Tubo de Laser Yong Li - 100w R5',
                     'pago_na_china': 1200,
                     'reminmbi': 6.84,
                     'dolar_cotado': 3.89,
                     'impostos_na_china': 0,
                     'porcentagem_importacao': 0.52,
                     'coeficiente': 0.50, }
        self.client.force_login(self.user_gerente)
        response = self.client.post(reverse('product_create', kwargs={'codigo': 'TYL-1100'}), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/products/product/update/TYL-1100/')
