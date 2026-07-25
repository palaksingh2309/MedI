import json
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

    def test_predict_insufficient_symptoms(self):
        # Log in first
        self.client.login(username='testpatient', password='testpassword123')
        
        # Test with fewer than 3 symptoms
        payload = {
            "symptoms": ["stomach_pain"],
            "severity": "mild",
            "duration": 2
        }
        response = self.client.post(
            reverse('prediction:predict'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertFalse(data["sufficientSymptoms"])
        self.assertIsNone(data["prediction"])
        self.assertGreater(len(data["followUpQuestions"]), 0)
        self.assertIn("symptom", data["followUpQuestions"][0])
        self.assertIn("question", data["followUpQuestions"][0])

    def test_rule_based_check_stomach_pain_drug_reaction(self):
        self.client.login(username='testpatient', password='testpassword123')
        
        # 1 symptom (stomach pain) -> should fail sufficiency check and not predict Drug Reaction
        payload = {
            "symptoms": ["stomach_pain"],
            "severity": "mild",
            "duration": 1
        }
        response = self.client.post(
            reverse('prediction:predict'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = response.json()
        self.assertFalse(data["sufficientSymptoms"])
        
        # 3 symptoms that are mostly generic and stomach_pain is present
        # Verify that Drug Reaction is not predicted or confidence is below 75%
        payload = {
            "symptoms": ["stomach_pain", "mild_fever", "headache"],
            "severity": "mild",
            "duration": 1
        }
        response = self.client.post(
            reverse('prediction:predict'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = response.json()
        self.assertTrue(data["sufficientSymptoms"])
        self.assertIsNone(data["prediction"]) # confidence < 75% due to generic symptoms

    def test_severity_and_duration_alerts(self):
        self.client.login(username='testpatient', password='testpassword123')
        
        # Severe symptoms -> emergency warning and consultation recommendation
        payload = {
            "symptoms": ["vomiting", "headache", "nausea"],
            "severity": "severe",
            "duration": 2
        }
        response = self.client.post(
            reverse('prediction:predict'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = response.json()
        self.assertIsNotNone(data["emergencyWarning"])
        self.assertIn("emergency", data["emergencyWarning"].lower())
        self.assertIn("consult", data["recommendation"].lower())

        # Persistent symptoms (duration >= 7) -> consultation recommendation
        payload = {
            "symptoms": ["vomiting", "headache", "nausea"],
            "severity": "mild",
            "duration": 8
        }
        response = self.client.post(
            reverse('prediction:predict'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = response.json()
        self.assertIsNone(data["emergencyWarning"])
        self.assertIn("persisted", data["recommendation"].lower())
