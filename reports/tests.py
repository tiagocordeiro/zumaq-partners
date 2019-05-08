from django.contrib.auth.models import AnonymousUser, User, Group
from django.test import RequestFactory, TestCase, Client

from .views import reports_dashboard, products_report


class ReportsDashboardViewTest(TestCase):
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

    # Testes para dashboard de relatórios
    def test_reports_dashboard_anonimo(self):
        request = self.factory.get('/reports/dashboard/')
        request.user = AnonymousUser()

        response = reports_dashboard(request)
        self.assertEqual(response.status_code, 302)

    def test_reports_dashboard_logado_parceiro(self):
        request = self.factory.get('/reports/dashboard/')
        request.user = self.user_parceiro

        response = reports_dashboard(request)
        self.assertEqual(response.status_code, 302)

    def test_reports_dashboard_logado_gerente(self):
        request = self.factory.get('/reports/dashboard/')
        request.user = self.user_gerente

        response = reports_dashboard(request)
        self.assertEqual(response.status_code, 200)

    # Testa views de ralatório de produtos
    def test_report_products_anonimo(self):
        request = self.factory.get('/reports/products/')
        request.user = AnonymousUser()

        response = products_report(request)
        self.assertEqual(response.status_code, 302)

    def test_report_products_logado_parceiro(self):
        request = self.factory.get('/reports/products/')
        request.user = self.user_parceiro

        response = products_report(request)
        self.assertEqual(response.status_code, 302)

    def test_report_products_logado_gerente(self):
        request = self.factory.get('/reports/products/')
        request.user = self.user_gerente

        response = products_report(request)
        self.assertEqual(response.status_code, 200)

    def test_report_products_ativos_logado_gerente(self):
        request = self.factory.get('/reports/products/ativos/')
        request.user = self.user_gerente

        response = products_report(request)
        self.assertEqual(response.status_code, 200)
