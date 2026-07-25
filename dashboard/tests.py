from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from .models import DailyWellness, HealthProfile
import datetime
import json

User = get_user_model()

class DashboardViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testpatient', password='TestPassword123')
        # HealthProfile is created automatically by signal

    def test_dashboard_view_no_logs(self):
        self.client.login(username='testpatient', password='TestPassword123')
        url = reverse('dashboard:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Verify chart labels are exactly 7
        labels = json.loads(response.context['chart_labels'])
        self.assertEqual(len(labels), 7)
        
        # Verify all telemetry datasets are padded to length 7
        water = json.loads(response.context['chart_water'])
        sleep = json.loads(response.context['chart_sleep'])
        exercise = json.loads(response.context['chart_exercise'])
        steps = json.loads(response.context['chart_steps'])
        
        self.assertEqual(len(water), 7)
        self.assertEqual(len(sleep), 7)
        self.assertEqual(len(exercise), 7)
        self.assertEqual(len(steps), 7)
        
        # Verify values are 0
        self.assertEqual(water, [0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(sleep, [0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(exercise, [0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(steps, [0, 0, 0, 0, 0, 0, 0])

    def test_dashboard_view_partial_logs(self):
        self.client.login(username='testpatient', password='TestPassword123')
        
        # Create a log for today and yesterday
        today = timezone.localdate()
        yesterday = today - datetime.timedelta(days=1)
        
        DailyWellness.objects.create(user=self.user, date=today, water_intake=1500, sleep_hours=7.0, exercise_duration=30, steps=8000)
        DailyWellness.objects.create(user=self.user, date=yesterday, water_intake=2000, sleep_hours=8.0, exercise_duration=45, steps=10000)
        
        url = reverse('dashboard:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        water = json.loads(response.context['chart_water'])
        sleep = json.loads(response.context['chart_sleep'])
        exercise = json.loads(response.context['chart_exercise'])
        steps = json.loads(response.context['chart_steps'])
        
        self.assertEqual(len(water), 7)
        self.assertEqual(len(sleep), 7)
        self.assertEqual(len(exercise), 7)
        self.assertEqual(len(steps), 7)
        
        # The last element should be today's log, second to last yesterday's, others 0
        self.assertEqual(water[-1], 1500)
        self.assertEqual(water[-2], 2000)
        self.assertEqual(water[0], 0)
        
        self.assertEqual(sleep[-1], 7.0)
        self.assertEqual(sleep[-2], 8.0)
        self.assertEqual(sleep[0], 0)

        self.assertEqual(exercise[-1], 30)
        self.assertEqual(exercise[-2], 45)
        self.assertEqual(exercise[0], 0)

        self.assertEqual(steps[-1], 8000)
        self.assertEqual(steps[-2], 10000)
        self.assertEqual(steps[0], 0)

    def test_update_wellness_get_redirects(self):
        self.client.login(username='testpatient', password='TestPassword123')
        url = reverse('dashboard:update_wellness')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('dashboard:index'))

