import base64               # for decoding base64 image
import tempfile             # for setting up tempdir for media

from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO

from django.contrib.auth.models import AnonymousUser, User, Group
from django.test import RequestFactory, TestCase, Client, override_settings

from .models import UserProfile
from .views import dashboard, profile_update


class DashboardViewTest(TestCase):
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

    def test_dashboard_anonimo(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()

        response = dashboard(request)
        self.assertEqual(response.status_code, 302)

    def test_dashboard_logado(self):
        request = self.factory.get('/')
        request.user = self.user_parceiro

        response = dashboard(request)
        self.assertEqual(response.status_code, 200)


class ProfileUpdateViewTest(TestCase):
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

        # User Profile Parceiro
        self.user_profile_parceiro = UserProfile.objects.create(user=self.user_parceiro, avatar=TEST_IMAGE)

    def test_profile_update_anonimo(self):
        request = self.factory.get('/profile/update/')
        request.user = AnonymousUser()

        response = profile_update(request)
        self.assertEqual(response.status_code, 302)

    def test_profile_update_logado(self):
        request = self.factory.get('/profile/update/')
        request.user = self.user_parceiro

        response = profile_update(request)
        self.assertEqual(response.status_code, 200)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_user_profile_update_name(self):
        image = InMemoryUploadedFile(
            BytesIO(base64.b64decode(TEST_IMAGE)),  # use io.BytesIO
            field_name='tempfile',
            name='tempfile.png',
            content_type='image/png',
            size=len(TEST_IMAGE),
            charset='utf-8',
        )

        data = {
            'first_name': 'Joe',
            'last_name': 'Forest',
            'email': 'joe@foo.bar',
            'userprofile-TOTAL_FORMS': 1,
            'userprofile-INITIAL_FORMS': 1,
            'userprofile-MIN_NUM_FORMS': 0,
            'userprofile-MAX_NUM_FORMS': 1,
            'userprofile-0-avatar': image,
            'userprofile-0-id': 1,
            'userprofile-0-user': 2,
        }

        self.client.force_login(self.user_parceiro)
        request = self.client.get('/profile/update/')

        self.assertEqual(request.status_code, 200)

        response = self.client.post('/profile/update/', data=data, instance=self.user_parceiro)

        self.user_parceiro.refresh_from_db()
        # self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user_parceiro.first_name, 'Joe')


TEST_IMAGE = '''
R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7
'''.strip()
