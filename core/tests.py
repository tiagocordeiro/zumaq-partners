from django.contrib.auth.models import AnonymousUser, User, Group
from django.test import RequestFactory, TestCase

from .views import dashboard, profile_update


class DashboardViewTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')
        self.group = Group.objects.create(name='Parceiro')
        self.group.user_set.add(self.user)

    def test_dashboard_anonimo(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()

        response = dashboard(request)
        self.assertEqual(response.status_code, 302)

    def test_dashboard_logado(self):
        request = self.factory.get('/')
        request.user = self.user

        response = dashboard(request)
        self.assertEqual(response.status_code, 200)


class ProfileUpdateViewTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')
        self.group = Group.objects.create(name='Parceiro')
        self.group.user_set.add(self.user)

    def test_profile_update_anonimo(self):
        request = self.factory.get('/profile/update/')
        request.user = AnonymousUser()

        response = profile_update(request)
        self.assertEqual(response.status_code, 302)

    def test_profile_update_logado(self):
        request = self.factory.get('/profile/update/')
        request.user = self.user

        response = profile_update(request)
        self.assertEqual(response.status_code, 200)
