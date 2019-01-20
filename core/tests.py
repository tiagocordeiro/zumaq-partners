import base64  # for decoding base64 image
import tempfile  # for setting up tempdir for media

from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO

from django.contrib.auth.models import AnonymousUser, User, Group
from django.test import RequestFactory, TestCase, Client, override_settings
from django.urls import reverse

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
        image_thumb = '''
                R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7
                '''.strip()

        self.image = InMemoryUploadedFile(
            BytesIO(base64.b64decode(image_thumb)),  # use io.BytesIO
            field_name='tempfile',
            name='tempfile.png',
            content_type='image/png',
            size=len(image_thumb),
            charset='utf-8',
        )

        self.user_profile_parceiro = UserProfile.objects.create(user=self.user_parceiro, avatar=str(self.image))

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
        data = {
            'first_name': 'Joe',
            'last_name': 'Forest',
            'email': 'joe@foo.bar',
            'userprofile-TOTAL_FORMS': 1,
            'userprofile-INITIAL_FORMS': 1,
            'userprofile-MIN_NUM_FORMS': 0,
            'userprofile-MAX_NUM_FORMS': 1,
            'userprofile-0-id': self.user_profile_parceiro.id,
            'userprofile-0-user': self.user_parceiro.id,
        }

        self.client.force_login(self.user_parceiro)
        request = self.client.get('/profile/update/')

        self.assertEqual(request.status_code, 200)

        response = self.client.post('/profile/update/', data=data, instance=self.user_parceiro)

        self.user_parceiro.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user_parceiro.first_name, 'Joe')


class ParceirosViewsTests(TestCase):
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
        image_thumb = '''
                R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7
                '''.strip()

        self.image = InMemoryUploadedFile(
            BytesIO(base64.b64decode(image_thumb)),  # use io.BytesIO
            field_name='tempfile',
            name='tempfile.png',
            content_type='image/png',
            size=len(image_thumb),
            charset='utf-8',
        )

        self.user_profile_parceiro = UserProfile.objects.create(user=self.user_parceiro, avatar=str(self.image))

    def test_view_list_parceiros(self):
        self.client.force_login(self.user_gerente)
        request = self.client.get(reverse('parceiro_list'))

        self.assertEqual(request.status_code, 200)

        # Adiciona novo parceiro
        novo_parceiro = User.objects.create_user(username='neo', email='neo@…', password='top_secret')
        self.group_parceiro.user_set.add(novo_parceiro)

        request = self.client.get(reverse('parceiro_list'))
        self.assertEqual(request.status_code, 200)
        parceiros = User.objects.filter(groups__name__in=['Parceiro'])
        parceiros.delete()

        request = self.client.get(reverse('parceiro_list'))
        self.assertEqual(request.status_code, 200)

    def test_list_parceiros_nao_gerente(self):
        self.client.force_login(self.user_parceiro)
        request = self.client.get(reverse('parceiro_list'))

        self.assertEqual(request.status_code, 302)

    def test_view_cadastro_parceiro(self):
        self.client.force_login(self.user_gerente)
        request = self.client.get(reverse('parceiro_cadastro'))

        self.assertEqual(request.status_code, 200)

    def test_view_cadastro_parceiro_post(self):
        new_user = {'username': 'newuser',
                    'email': 'newuser@foo.bar',
                    'first_name': 'New',
                    'last_name': 'User',
                    'password1': 'top_secret',
                    'password2': 'top_secret', }

        parceiros = User.objects.filter(groups__name__in=['Parceiro'])
        self.assertEqual(len(parceiros), 1)

        self.client.force_login(self.user_gerente)
        response = self.client.post(reverse('parceiro_cadastro'), data=new_user)

        new_user = User.objects.get(username='newuser')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(new_user.first_name, 'New')

        parceiros = User.objects.filter(groups__name__in=['Parceiro'])
        self.assertEqual(len(parceiros), 2)

    def test_view_parceiro_create_get_nao_gerente(self):
        self.client.force_login(self.user_parceiro)
        request = self.client.get(reverse('parceiro_create'))

        self.assertEqual(request.status_code, 302)

    def test_view_parceiro_create_get_gerente(self):
        self.client.force_login(self.user_gerente)
        request = self.client.get(reverse('parceiro_create'))

        self.assertEqual(request.status_code, 200)

    def test_view_parceiro_create_by_gerente(self):
        novo_parceiro = {'username': 'newpartner',
                         'email': 'newpartner@foo.bar',
                         'first_name': 'NewP',
                         'last_name': 'User',
                         'password1': 'top_secret',
                         'password2': 'top_secret', }

        parceiros = User.objects.filter(groups__name__in=['Parceiro'])
        self.assertEqual(len(parceiros), 1)

        self.client.force_login(self.user_gerente)
        response = self.client.post(reverse('parceiro_create'), data=novo_parceiro)

        novo_parceiro = User.objects.get(username='newpartner')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(novo_parceiro.first_name, 'NewP')

        parceiros = User.objects.filter(groups__name__in=['Parceiro'])
        self.assertEqual(len(parceiros), 2)
