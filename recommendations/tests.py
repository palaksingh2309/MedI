from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth import get_user_model
from recommendations.models import Specialist, Disease, Medicine, RecommendationHistory
from prediction.models import PredictionHistory

User = get_user_model()

class RecommendationModelsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.specialist = Specialist.objects.create(
            specialist='Dermatologist',
            description='Deals with skin disorders.'
        )
        self.disease = Disease.objects.create(
            disease_name='Acne',
            description='Acne description.',
            causes='Blocked hair follicles.',
            symptoms=['pimples', 'blackheads'],
            precautions=['Wash face', 'Don\'t pop'],
            diet={'recommended': ['Zinc rich foods'], 'avoid': ['Dairy']},
            home_remedies=['Tea tree oil'],
            specialist='Dermatologist'
        )
        self.medicine = Medicine.objects.create(
            disease=self.disease,
            medicine_name='Benzoyl Peroxide',
            medicine_type='OTC',
            otc=True,
            description='Kills bacteria.',
            precautions='Can dry skin.'
        )

    def test_model_creation(self):
        self.assertEqual(Specialist.objects.count(), 1)
        self.assertEqual(Disease.objects.count(), 1)
        self.assertEqual(Medicine.objects.count(), 1)

    def test_string_representation(self):
        self.assertEqual(str(self.specialist), 'Dermatologist')
        self.assertEqual(str(self.disease), 'Acne')
        self.assertEqual(str(self.medicine), 'Benzoyl Peroxide (OTC)')

    def test_recommendation_history_creation(self):
        prediction = PredictionHistory.objects.create(
            user=self.user,
            symptoms=['pimples'],
            prediction='Acne',
            confidence=85.0
        )
        history = RecommendationHistory.objects.create(
            user=self.user,
            prediction=prediction,
            disease='Acne',
            specialist='Dermatologist'
        )
        self.assertEqual(RecommendationHistory.objects.count(), 1)
        self.assertEqual(str(history), f"Recommendation of Acne for testuser at {history.viewed_at}")


class SeedingCommandTestCase(TestCase):
    def test_seed_recommendations_command(self):
        # Verify initial database is empty of seeded entries (excluding setUp if any)
        Specialist.objects.all().delete()
        Disease.objects.all().delete()
        Medicine.objects.all().delete()

        # Call management command
        call_command('seed_recommendations')

        # Verify Specialists
        specialists_count = Specialist.objects.count()
        self.assertEqual(specialists_count, 23)

        # Verify Diseases
        diseases_count = Disease.objects.count()
        self.assertEqual(diseases_count, 41)

        # Verify Medicines
        medicines_count = Medicine.objects.count()
        self.assertEqual(medicines_count, 13)

        # Verify specific details of a seeded disease
        common_cold = Disease.objects.get(disease_name='Common Cold')
        self.assertTrue(any('rest' in r.lower() for r in common_cold.home_remedies))
        self.assertEqual(common_cold.specialist, 'General Physician')
        self.assertEqual(common_cold.diet['avoid'], ['Ice cream', 'Cold drinks', 'Alcohol', 'Sugary foods'])

        # Verify related OTC medicines
        cold_meds = common_cold.medicines.all()
        self.assertGreater(cold_meds.count(), 0)
        self.assertTrue(all(med.otc for med in cold_meds))

        # Run again to ensure no duplication
        call_command('seed_recommendations')
        self.assertEqual(Specialist.objects.count(), 23)
        self.assertEqual(Disease.objects.count(), 41)
        self.assertEqual(Medicine.objects.count(), 13)


import json
from django.urls import reverse

class RecommendationsViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.disease = Disease.objects.create(
            disease_name='Acne',
            description='Acne description.',
            causes='Blocked hair follicles.',
            symptoms=['pimples', 'blackheads'],
            precautions=['Wash face', 'Don\'t pop'],
            diet={'recommended': ['Zinc rich foods'], 'avoid': ['Dairy']},
            home_remedies=['Tea tree oil'],
            specialist='Dermatologist'
        )
        self.prediction = PredictionHistory.objects.create(
            user=self.user,
            symptoms=['pimples'],
            prediction='Acne',
            confidence=85.0
        )

    def test_recommendations_api_requires_login(self):
        url = reverse('recommendations:api_recommendations')
        response = self.client.post(url, json.dumps({'prediction_id': str(self.prediction.id)}), content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_recommendations_api_success(self):
        self.client.login(username='testuser', password='password123')
        url = reverse('recommendations:api_recommendations')
        response = self.client.post(url, json.dumps({'prediction_id': str(self.prediction.id)}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['disease'], 'Acne')
        self.assertEqual(data['specialist'], 'Dermatologist')
        self.assertEqual(data['precautions'], ['Wash face', 'Don\'t pop'])
        
    def test_hospitals_api_requires_login(self):
        url = reverse('recommendations:api_hospitals')
        response = self.client.post(url, json.dumps({'latitude': 23.25, 'longitude': 77.41}), content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_hospitals_api_success(self):
        self.client.login(username='testuser', password='password123')
        url = reverse('recommendations:api_hospitals')
        response = self.client.post(url, json.dumps({'latitude': 23.25, 'longitude': 77.41}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreater(len(data), 0)
        self.assertIn('name', data[0])

