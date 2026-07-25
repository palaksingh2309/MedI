from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

class Prediction(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='predictions'
    )
    symptoms = models.TextField(help_text="Symptoms description or comma-separated list")
    predicted_disease = models.CharField(max_length=255)
    confidence_score = models.FloatField(help_text="Confidence level as a percentage or fraction")
    recommendations = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"{self.predicted_disease} prediction for {username} on {self.created_at.strftime('%Y-%m-%d')}"

class SavedClinic(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_clinics'
    )
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    rating = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} saved by {self.user.username}"

class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_messages'
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role.capitalize()} message by {self.user.username} at {self.created_at}"

class MedicalReport(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='medical_reports'
    )
    file = models.FileField(upload_to='medical_reports/')
    summary = models.TextField(blank=True, null=True, help_text="AI generated summary of the medical report")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.user.username} uploaded on {self.created_at.strftime('%Y-%m-%d')}"


class HealthProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='health_profile'
    )
    height = models.FloatField(null=True, blank=True, help_text="Height in cm")
    weight = models.FloatField(null=True, blank=True, help_text="Weight in kg")
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    existing_conditions = models.TextField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=100, blank=True, null=True)
    fitness_goal = models.CharField(max_length=100, blank=True, null=True)
    water_goal = models.FloatField(default=2000, help_text="Water goal in ml")
    sleep_goal = models.FloatField(default=8, help_text="Sleep goal in hours")
    updated_at = models.DateTimeField(auto_now=True)

    def get_bmi(self):
        if self.height and self.weight:
            height_m = self.height / 100.0
            return round(self.weight / (height_m ** 2), 1)
        return None

    def get_bmi_category(self):
        bmi = self.get_bmi()
        if not bmi:
            return "N/A"
        if bmi < 18.5:
            return "Underweight"
        elif 18.5 <= bmi < 25:
            return "Healthy weight"
        elif 25 <= bmi < 30:
            return "Overweight"
        else:
            return "Obese"

    def get_bmi_tips(self):
        cat = self.get_bmi_category()
        if cat == "Underweight":
            return "Focus on nutrient-dense meals and strength training to build lean mass."
        elif cat == "Healthy weight":
            return "Great job! Keep doing what you are doing. Maintain a balanced diet and regular physical activity."
        elif cat == "Overweight":
            return "Consider a balanced calorie deficit and 150 minutes of moderate exercise per week."
        elif cat == "Obese":
            return "Consult a health professional for personalized guidance on nutrition, fitness, and lifestyle changes."
        return "Please enter your height and weight in your Health Profile to calculate BMI and receive recommendations."

    def __str__(self):
        return f"Health Profile for {self.user.username}"


class DailyWellness(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='daily_wellness_records'
    )
    date = models.DateField(default=timezone.now)
    water_intake = models.FloatField(default=0, help_text="Water intake in ml")
    sleep_hours = models.FloatField(default=0)
    exercise_duration = models.IntegerField(default=0, help_text="Exercise duration in minutes")
    steps = models.IntegerField(default=0)
    mood = models.CharField(max_length=50, blank=True, null=True)
    stress_level = models.IntegerField(default=1)
    heart_rate = models.IntegerField(null=True, blank=True, help_text="Heart rate in bpm")
    blood_pressure = models.CharField(max_length=20, blank=True, null=True, help_text="e.g. 120/80")
    blood_sugar = models.FloatField(null=True, blank=True, help_text="Blood sugar in mg/dL")
    calories_consumed = models.IntegerField(default=0)
    fruits_veg_servings = models.IntegerField(default=0)
    screen_time = models.FloatField(default=0, help_text="Screen time in hours")

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"Wellness for {self.user.username} on {self.date}"

    def get_health_score(self):
        profile = getattr(self.user, 'health_profile', None)
        water_goal = profile.water_goal if profile else 2000
        sleep_goal = profile.sleep_goal if profile else 8
        
        score = 0
        
        # 1. BMI (25 pts)
        if profile:
            bmi = profile.get_bmi()
            if bmi:
                if 18.5 <= bmi < 25.0:
                    score += 25
                elif 25.0 <= bmi < 30.0 or 17.0 <= bmi < 18.5:
                    score += 18
                else:
                    score += 10
            else:
                score += 15
        else:
            score += 15
            
        # 2. Water (20 pts)
        if water_goal > 0:
            score += int(min(self.water_intake / water_goal, 1.0) * 20)
        else:
            score += 20
            
        # 3. Sleep (20 pts)
        if sleep_goal > 0:
            score += int(min(self.sleep_hours / sleep_goal, 1.0) * 20)
        else:
            score += 20
            
        # 4. Exercise (20 pts)
        score += int(min(self.exercise_duration / 30.0, 1.0) * 20)
        
        # 5. Steps (15 pts)
        score += int(min(self.steps / 10000.0, 1.0) * 15)
        
        return min(max(score, 10), 100)


# Signals to auto-create HealthProfile
User = get_user_model()

@receiver(post_save, sender=User)
def create_user_health_profile(sender, instance, created, **kwargs):
    if created:
        HealthProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_health_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'health_profile'):
        HealthProfile.objects.create(user=instance)
    else:
        instance.health_profile.save()


