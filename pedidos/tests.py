from django.contrib.auth.models import User, Group
from django.test import TestCase, RequestFactory, Client
from django.urls import reverse

from products.models import Produto, CustomCoeficiente, CustomCoeficienteItens
from pedidos.models import Pedido
from pedidos.views import pedidos_list, pedido_add_item, pedido_aberto
from django.contrib.messages.storage.fallback import FallbackStorage


class PedidosTestCase(TestCase):
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

        # Produto
        self.product = Produto.objects.create(codigo='TYL-1080',
                                              descricao='Tubo de Laser Yong Li - 80w - R3',
                                              pago_na_china=880,
                                              reminmbi=6.84,
                                              dolar_cotado=3.89,
                                              impostos_na_china=0,
                                              porcentagem_importacao=0.52,
                                              coeficiente=0.50)

        # Custom Coeficiente Parceiro
        self.custom_coeficiente = CustomCoeficiente.objects.create(parceiro=self.user_parceiro)
        # Custom Coeficiente Parceiro -> Produto
        self.custom_coeficiente_item = CustomCoeficienteItens.objects.create(parceiro=self.custom_coeficiente,
                                                                             produto=self.product,
                                                                             coeficiente=0.10)

        self.pedido_aberto = Pedido.objects.create(parceiro=self.user_parceiro)

    def test_pedido_add_item(self):
        item = self.product

        request = self.factory.post(reverse('pedido_add_item', kwargs={'codigo': item.codigo}))
        request.user = self.user_parceiro
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = pedido_add_item(request, codigo=item.codigo)
        self.assertEqual(response.status_code, 302)

    def test_pedido_aberto_view_parceiro(self):
        pedido = self.pedido_aberto
        self.assertEqual(pedido.pedidoitem_set.values().count(), 0)
        self.test_pedido_add_item()
        self.assertEqual(pedido.pedidoitem_set.values().count(), 1)

        request = self.factory.get(reverse('pedido_aberto'))
        request.user = self.user_parceiro

        response = pedido_aberto(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(pedido.get_status_display(), 'Aberto')

    def test_pedidos_list_view_anonimo(self):
        self.client.logout()
        response = self.client.get(reverse('pedidos_list'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/pedido/list/',
                             status_code=302, target_status_code=200)

    def test_pedidos_list_view_gerente(self):
        request = self.factory.get(reverse('pedidos_list'))
        request.user = self.user_gerente

        response = pedidos_list(request)
        self.assertEqual(response.status_code, 200)

    def test_pedidos_list_view_parceiro(self):
        request = self.factory.get(reverse('pedidos_list'))
        request.user = self.user_parceiro

        response = pedidos_list(request)
        self.assertEqual(response.status_code, 200)
