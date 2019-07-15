from django.contrib.auth.models import User, Group
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import TestCase, RequestFactory, Client
from django.urls import reverse

from pedidos.models import Pedido
from pedidos.views import pedidos_list, pedido_add_item, pedido_aberto, pedido_checkout, pedido_details, \
    pedido_export_pdf, pedido_delivery_term_pdf, pedido_delivery_term_with_order_pdf
from products.models import Produto, CustomCoeficiente, CustomCoeficienteItens


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

        # User Parceiro2
        self.user_parceiro2 = User.objects.create_user(username='robert', email='robert@…', password='top_secret')
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

    def test_pedido_checkout(self):
        pedido = self.pedido_aberto
        request = self.factory.get(reverse('pedido_checkout', kwargs={'pk': pedido.pk}))
        request.user = self.user_parceiro
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        self.assertEqual(pedido.status, 0)

        response = pedido_checkout(request, pedido.pk)

        self.assertEqual(response.status_code, 200)

        pedido.refresh_from_db()
        self.assertEqual(pedido.status, 1)

    def test_pedido_checkout_not_owner(self):
        """
        Testa checkout quando o usuário não é dono do pedido em aberto.
        :return: Deve retornar status_code = 302 e redirecionar para dashboard.
        """
        pedido = self.pedido_aberto
        request = self.factory.get(reverse('pedido_checkout', kwargs={'pk': pedido.pk}))
        request.user = self.user_gerente

        self.assertEqual(pedido.status, 0)

        response = pedido_checkout(request, pedido.pk)
        self.assertEqual(response.status_code, 302)

        pedido.refresh_from_db()
        self.assertEqual(pedido.status, 0)

    def test_pedido_detais_view_by_owner(self):
        pedido = self.pedido_aberto
        self.assertEqual(pedido.pedidoitem_set.values().count(), 0)
        self.test_pedido_add_item()
        self.assertEqual(pedido.pedidoitem_set.values().count(), 1)
        self.test_pedido_checkout()

        request = self.factory.get(reverse('pedido_details', kwargs={'pk': pedido.pk}))
        request.user = self.user_parceiro

        response = pedido_details(request, pedido.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(pedido.get_status_display(), 'Enviado')

    def test_pedido_detais_view_not_owner(self):
        pedido = self.pedido_aberto
        self.assertEqual(pedido.pedidoitem_set.values().count(), 0)
        self.test_pedido_add_item()
        self.assertEqual(pedido.pedidoitem_set.values().count(), 1)
        self.test_pedido_checkout()

        request = self.factory.get(reverse('pedido_details', kwargs={'pk': pedido.pk}))
        request.user = self.user_parceiro2

        response = pedido_details(request, pedido.pk)
        self.assertEqual(response.status_code, 302)

    def test_pedido_detais_view_as_gerente(self):
        pedido = self.pedido_aberto
        self.assertEqual(pedido.pedidoitem_set.values().count(), 0)
        self.test_pedido_add_item()
        self.assertEqual(pedido.pedidoitem_set.values().count(), 1)
        self.test_pedido_checkout()

        request = self.factory.get(reverse('pedido_details', kwargs={'pk': pedido.pk}))
        request.user = self.user_gerente

        response = pedido_details(request, pedido.pk)
        self.assertEqual(response.status_code, 200)

    def test_pedido_export_pdf_anonimo(self):
        pedido = self.pedido_aberto
        self.assertEqual(pedido.pedidoitem_set.values().count(), 0)
        self.test_pedido_add_item()
        self.assertEqual(pedido.pedidoitem_set.values().count(), 1)
        self.test_pedido_checkout()

        self.client.logout()
        response = self.client.get(reverse('pedido_export_pdf', kwargs={'pk': pedido.pk}))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response,
                             f'/accounts/login/?next=/pedido/export/pdf/{pedido.pk}/',
                             status_code=302,
                             target_status_code=200)

    def test_pedido_export_pdf_as_gerente(self):
        pedido = self.pedido_aberto
        self.assertEqual(pedido.pedidoitem_set.values().count(), 0)
        self.test_pedido_add_item()
        self.assertEqual(pedido.pedidoitem_set.values().count(), 1)
        self.test_pedido_checkout()

        request = self.factory.get(reverse('pedido_export_pdf', kwargs={'pk': pedido.pk}))
        request.user = self.user_gerente

        response = pedido_export_pdf(request, pedido.pk)
        self.assertEqual(response.status_code, 200)

    def test_pedido_export_pdf_not_owner(self):
        pedido = self.pedido_aberto
        self.assertEqual(pedido.pedidoitem_set.values().count(), 0)
        self.test_pedido_add_item()
        self.assertEqual(pedido.pedidoitem_set.values().count(), 1)
        self.test_pedido_checkout()

        request = self.factory.get(reverse('pedido_export_pdf', kwargs={'pk': pedido.pk}))
        request.user = self.user_parceiro2

        response = pedido_export_pdf(request, pedido.pk)
        self.assertEqual(response.status_code, 302)

    def test_pedido_export_delivery_term_pdf_anonimo(self):
        pedido = self.pedido_aberto
        self.assertEqual(pedido.pedidoitem_set.values().count(), 0)
        self.test_pedido_add_item()
        self.assertEqual(pedido.pedidoitem_set.values().count(), 1)
        self.test_pedido_checkout()

        self.client.logout()
        response = self.client.get(reverse('pedido_export_delivery_term_pdf', kwargs={'pk': pedido.pk}))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response,
                             f'/accounts/login/?next=/pedido/export/pdf/deliveryterm/{pedido.pk}/',
                             status_code=302,
                             target_status_code=200)

    def test_pedido_export_delivery_term_pdf_as_gerente(self):
        pedido = self.pedido_aberto
        self.assertEqual(pedido.pedidoitem_set.values().count(), 0)
        self.test_pedido_add_item()
        self.assertEqual(pedido.pedidoitem_set.values().count(), 1)
        self.test_pedido_checkout()

        request = self.factory.get(reverse('pedido_export_delivery_term_pdf', kwargs={'pk': pedido.pk}))
        request.user = self.user_gerente

        response = pedido_delivery_term_pdf(request, pedido.pk)
        self.assertEqual(response.status_code, 200)

    def test_pedido_export_delivery_term_pdf_not_owner(self):
        pedido = self.pedido_aberto
        self.assertEqual(pedido.pedidoitem_set.values().count(), 0)
        self.test_pedido_add_item()
        self.assertEqual(pedido.pedidoitem_set.values().count(), 1)
        self.test_pedido_checkout()

        request = self.factory.get(reverse('pedido_export_delivery_term_pdf', kwargs={'pk': pedido.pk}))
        request.user = self.user_parceiro2

        response = pedido_delivery_term_pdf(request, pedido.pk)
        self.assertEqual(response.status_code, 302)

    def test_pedido_export_complete_pdf_anonimo(self):
        pedido = self.pedido_aberto
        self.assertEqual(pedido.pedidoitem_set.values().count(), 0)
        self.test_pedido_add_item()
        self.assertEqual(pedido.pedidoitem_set.values().count(), 1)
        self.test_pedido_checkout()

        self.client.logout()
        response = self.client.get(reverse('pedido_export_complete_pdf', kwargs={'pk': pedido.pk}))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response,
                             f'/accounts/login/?next=/pedido/export/pdf/completo/{pedido.pk}/',
                             status_code=302,
                             target_status_code=200)

    def test_pedido_export_complete_pdf_as_gerente(self):
        pedido = self.pedido_aberto
        self.assertEqual(pedido.pedidoitem_set.values().count(), 0)
        self.test_pedido_add_item()
        self.assertEqual(pedido.pedidoitem_set.values().count(), 1)
        self.test_pedido_checkout()

        request = self.factory.get(reverse('pedido_export_complete_pdf', kwargs={'pk': pedido.pk}))
        request.user = self.user_gerente

        response = pedido_delivery_term_with_order_pdf(request, pedido.pk)
        self.assertEqual(response.status_code, 200)

    def test_pedido_export_complete_pdf_not_owner(self):
        pedido = self.pedido_aberto
        self.assertEqual(pedido.pedidoitem_set.values().count(), 0)
        self.test_pedido_add_item()
        self.assertEqual(pedido.pedidoitem_set.values().count(), 1)
        self.test_pedido_checkout()

        request = self.factory.get(reverse('pedido_export_complete_pdf', kwargs={'pk': pedido.pk}))
        request.user = self.user_parceiro2

        response = pedido_delivery_term_with_order_pdf(request, pedido.pk)
        self.assertEqual(response.status_code, 302)
