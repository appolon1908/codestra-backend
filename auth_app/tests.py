"""Source-only auth regressions: disposable PostgreSQL and no provider effects."""
from unittest.mock import Mock, patch
from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework_simplejwt.tokens import AccessToken
from .models import User
from .views import AuthViewSet, UserViewSet


class AuthSourceTests(TestCase):
    @classmethod
    def setUpClass(cls):
        db = settings.DATABASES['default']
        if db['HOST'] not in ('127.0.0.1', 'localhost') or not db['NAME'].startswith('test_'):
            raise RuntimeError('Auth source tests require disposable loopback test database')
        super().setUpClass()

    def setUp(self):
        self.factory = APIRequestFactory()
        self.provider_guard = patch('requests.sessions.Session.request', side_effect=AssertionError('Provider effects forbidden in source tests'))
        self.provider_guard.start()
        self.addCleanup(self.provider_guard.stop)
        self.user = User.objects.create_user(email='source@example.invalid', password='source-test-password', first_name='Source', last_name='Test', odoo_id=1)
        self.other = User.objects.create_user(email='other@example.invalid', password='other-test-password', first_name='Other', last_name='Test', odoo_id=2)

    def auth(self, action, payload):
        request = self.factory.post('/api/auth/' + action + '/', payload, format='json')
        return AuthViewSet.as_view({'post': action})(request)

    def test_password_stored_as_hash(self):
        self.assertNotEqual(self.user.password, 'source-test-password')
        self.assertTrue(self.user.check_password('source-test-password'))

    def test_login_signed_access_token_and_no_password_disclosure(self):
        response = self.auth('login_view', {'email': self.user.email, 'password': 'source-test-password'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(AccessToken(response.data['token']['access'])['user_id'], self.user.pk)
        self.assertNotIn('password', response.data['user'])

    def test_unknown_login_rejected(self):
        self.assertEqual(self.auth('login_view', {'email': 'missing@example.invalid', 'password': 'wrong'}).status_code, 400)

    def test_wrong_password_rejected_without_server_error(self):
        self.assertEqual(self.auth('login_view', {'email': self.user.email, 'password': 'wrong'}).status_code, 400)

    def test_anonymous_user_list_denied(self):
        response = UserViewSet.as_view({'get': 'list'})(self.factory.get('/api/auth/users/'))
        self.assertIn(response.status_code, (401, 403))

    def test_authenticated_me_uses_actual_user(self):
        request = self.factory.get('/api/auth/users/me/')
        force_authenticate(request, self.user)
        response = UserViewSet.as_view({'get': 'me'})(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], self.user.pk)
        self.assertNotIn('password', response.data)

    def test_regular_user_cannot_delete_another_account(self):
        request = self.factory.delete('/api/auth/users/' + self.other.pk + '/')
        force_authenticate(request, self.user)
        response = UserViewSet.as_view({'delete': 'destroy'})(request, pk=self.other.pk)
        self.assertIn(response.status_code, (403, 404))
        self.assertTrue(User.objects.filter(pk=self.other.pk).exists())

    def test_signup_provider_success_is_mocked_and_password_hashed(self):
        payload = {'email': 'signup@example.invalid', 'password': 'signup-test-password', 'first_name': 'New', 'last_name': 'User'}
        provider = Mock(status_code=200)
        provider.json.return_value = {'result': {'id': 99}}
        with patch('auth_app.views.requests.post', return_value=provider) as call:
            response = self.auth('signup', payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(call.call_count, 1)
        self.assertTrue(User.objects.get(email=payload['email']).check_password(payload['password']))

    def test_signup_invalid_input_does_not_call_provider(self):
        with patch('auth_app.views.requests.post') as call:
            response = self.auth('signup', {'email': 'invalid'})
        self.assertEqual(response.status_code, 400)
        call.assert_not_called()

    def test_logout_invalid_token_rejected(self):
        self.assertEqual(self.auth('logout', {'refresh': 'invalid'}).status_code, 400)
