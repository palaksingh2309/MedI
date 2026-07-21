# pyrefly: ignore [missing-import]
from django.test import TestCase
# pyrefly: ignore [missing-import]
from django.urls import reverse
# pyrefly: ignore [missing-import]
from django.contrib.auth import get_user_model

class CustomUserTests(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            username='testpatient',
            email='test@example.com',
            password='testpassword123',
            first_name='John',
            last_name='Doe',
            phone_number='1234567890'
        )
        self.assertEqual(user.username, 'testpatient')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.phone_number, '1234567890')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            username='adminpatient',
            email='admin@example.com',
            password='testpassword123'
        )
        self.assertEqual(admin_user.username, 'adminpatient')
        self.assertEqual(admin_user.email, 'admin@example.com')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

class PageRoutingTests(TestCase):
    def test_login_page_status_code(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_signup_page_status_code(self):
        response = self.client.get(reverse('accounts:signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')

    def test_dashboard_redirects_if_logged_out(self):
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login
        self.assertIn(reverse('accounts:login'), response.url)

    def test_profile_redirects_if_logged_out(self):
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login
        self.assertIn(reverse('accounts:login'), response.url)
