from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

class PredictionViewTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testpatient',
            email='test@example.com',
            password='testpassword123',
            first_name='John',
            last_name='Doe'
        )

    def test_predict_page_redirects_if_logged_out(self):
        # Access UI page without logging in - should redirect to login
        response = self.client.get(reverse('dashboard:predict_page'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)

    def test_predict_page_renders_for_logged_in_user(self):
        # Log in and check UI page renders correctly
        self.client.login(username='testpatient', password='testpassword123')
        response = self.client.get(reverse('dashboard:predict_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'prediction/predict.html')
        self.assertIn('symptoms', response.context)
        self.assertGreater(len(response.context['symptoms']), 0)

    def test_symptoms_list_api_returns_json(self):
        # Access symptoms list API
        response = self.client.get(reverse('prediction:symptoms_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = response.json()
        self.assertTrue(isinstance(data, list))
        self.assertGreater(len(data), 0)
        # Check first item structure
        self.assertIn('value', data[0])
        self.assertIn('label', data[0])
