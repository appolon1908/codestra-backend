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

    def mutate(self, actor, target, operation, **extra):
        if operation == 'update':
            payload = {'email': 'updated-' + target.email, 'first_name': 'Updated', 'last_name': 'Account', 'password': 'unused-write-only-password'}
            payload.update(extra)
            request = self.factory.put('/api/auth/users/' + target.pk + '/', payload, format='json')
            mapping = {'put': 'update'}
        else:
            request = self.factory.delete('/api/auth/users/' + target.pk + '/')
            mapping = {'delete': 'destroy'}
        force_authenticate(request, actor)
        return UserViewSet.as_view(mapping)(request, pk=target.pk)

    def grant_model_permission(self, actor, operation):
        from django.contrib.auth.models import Permission
        opts = User._meta
        actor.user_permissions.add(Permission.objects.get(content_type__app_label=opts.app_label, content_type__model=opts.model_name, codename=f'{operation}_{opts.model_name}'))

    def test_own_account_update_remains_allowed(self):
        self.assertEqual(self.mutate(self.user, self.user, 'update').status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertTrue(self.user.check_password('source-test-password'))

    def test_own_account_delete_remains_allowed(self):
        self.assertEqual(self.mutate(self.user, self.user, 'destroy').status_code, 204)
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())

    def test_regular_user_cross_account_update_denied(self):
        self.assertEqual(self.mutate(self.user, self.other, 'update').status_code, 403)
        self.other.refresh_from_db()
        self.assertEqual(self.other.first_name, 'Other')

    def test_staff_without_model_permission_cannot_update_other(self):
        self.user.is_staff = True
        self.user.save()
        self.assertEqual(self.mutate(self.user, self.other, 'update').status_code, 403)

    def test_staff_without_model_permission_cannot_delete_other(self):
        self.user.is_staff = True
        self.user.save()
        self.assertEqual(self.mutate(self.user, self.other, 'destroy').status_code, 403)
        self.assertTrue(User.objects.filter(pk=self.other.pk).exists())

    def test_superuser_can_update_other(self):
        self.user.is_superuser = True
        self.user.save()
        self.assertEqual(self.mutate(self.user, self.other, 'update').status_code, 200)

    def test_superuser_can_delete_other(self):
        self.user.is_superuser = True
        self.user.save()
        self.assertEqual(self.mutate(self.user, self.other, 'destroy').status_code, 204)

    def test_explicit_model_change_permission_allows_update(self):
        self.grant_model_permission(self.user, 'change')
        self.assertFalse(self.user.is_staff)
        self.assertEqual(self.mutate(self.user, self.other, 'update').status_code, 200)

    def test_explicit_model_delete_permission_allows_delete(self):
        self.grant_model_permission(self.user, 'delete')
        self.assertFalse(self.user.is_staff)
        self.assertEqual(self.mutate(self.user, self.other, 'destroy').status_code, 204)

    def test_change_permission_does_not_grant_delete(self):
        self.grant_model_permission(self.user, 'change')
        self.assertEqual(self.mutate(self.user, self.other, 'destroy').status_code, 403)

    def test_delete_permission_does_not_grant_update(self):
        self.grant_model_permission(self.user, 'delete')
        self.assertEqual(self.mutate(self.user, self.other, 'update').status_code, 403)

    def test_ordinary_own_account_privilege_fields_denied(self):
        for field in ('is_staff', 'is_superuser', 'is_active', 'is_admin', 'groups', 'user_permissions'):
            with self.subTest(field=field):
                self.assertEqual(self.mutate(self.user, self.user, 'update', **{field: True}).status_code, 403)
                self.user.refresh_from_db()
                self.assertFalse(self.user.is_staff)
                self.assertFalse(self.user.is_superuser)
                self.assertFalse(self.user.is_admin)

    def test_staff_own_account_privilege_fields_denied(self):
        self.user.is_staff = True
        self.user.save()
        self.assertEqual(self.mutate(self.user, self.user, 'update', is_superuser=True).status_code, 403)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_superuser)

    def test_existing_list_and_read_behavior_unchanged(self):
        for mapping, target in (({'get': 'list'}, None), ({'get': 'retrieve'}, self.other.pk)):
            request = self.factory.get('/api/auth/users/')
            force_authenticate(request, self.user)
            response = UserViewSet.as_view(mapping)(request, **({'pk': target} if target else {}))
            self.assertEqual(response.status_code, 200)

    def test_login_token_rejects_changed_signature(self):
        from rest_framework_simplejwt.exceptions import TokenError
        response = self.auth('login_view', {'email': self.user.email, 'password': 'source-test-password'})
        parts = response.data['token']['access'].split('.')
        parts[2] = ('A' if parts[2][0] != 'A' else 'B') + parts[2][1:]
        with self.assertRaises(TokenError):
            AccessToken('.'.join(parts))

    def test_login_token_rejects_wrong_key_algorithm_and_unsigned_input(self):
        import jwt
        from rest_framework_simplejwt.exceptions import TokenError
        response = self.auth('login_view', {'email': self.user.email, 'password': 'source-test-password'})
        payload = dict(AccessToken(response.data['token']['access']).payload)
        candidates = (
            jwt.encode(payload, 'different-disposable-source-signing-key', algorithm='HS256'),
            jwt.encode(payload, settings.SECRET_KEY, algorithm='HS384'),
            jwt.encode(payload, '', algorithm='none'),
        )
        for candidate in candidates:
            with self.subTest(kind=candidate.split('.')[0]):
                with self.assertRaises(TokenError):
                    AccessToken(candidate)

    def test_access_token_rejects_expired_and_refresh_types(self):
        from datetime import timedelta
        from rest_framework_simplejwt.tokens import RefreshToken
        from rest_framework_simplejwt.exceptions import TokenError
        expired = AccessToken.for_user(self.user)
        expired.set_exp(lifetime=timedelta(seconds=-60))
        for candidate in (str(expired), str(RefreshToken.for_user(self.user))):
            with self.assertRaises(TokenError):
                AccessToken(candidate)

    def test_every_owned_application_module_imports_without_provider_or_worker_effects(self):
        from contextlib import ExitStack
        from importlib import import_module
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        packages = {path.name for path in root.iterdir() if path.is_dir() and (path / '__init__.py').is_file()}
        modules = []
        for path in root.rglob('*.py'):
            relative = path.relative_to(root)
            if relative.parts[0] not in packages or 'migrations' in relative.parts or path.name.startswith('test'):
                continue
            parts = list(relative.with_suffix('').parts)
            if parts[-1] == '__init__':
                parts.pop()
            modules.append('.'.join(parts))
        with ExitStack() as stack:
            for target in ('socket.socket.connect', 'socket.create_connection', 'subprocess.Popen', 'smtplib.SMTP', 'celery.app.task.Task.apply_async', 'django.db.backends.utils.CursorWrapper.execute'):
                stack.enter_context(patch(target, side_effect=AssertionError('Import-time network/database/provider/process effects forbidden')))
            for module in sorted(set(modules)):
                with self.subTest(module=module):
                    import_module(module)
        self.assertGreater(len(set(modules)), 50)
