import uuid
from django.db import models
from django.conf import settings

class Specialist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    specialist = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'specialists'

    def __str__(self):
        return self.specialist

class Disease(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    disease_name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    causes = models.TextField(blank=True, null=True)
    symptoms = models.JSONField(default=list, blank=True, help_text="List of typical symptoms")
    precautions = models.JSONField(default=list, blank=True, help_text="List of precautions")
    diet = models.JSONField(default=dict, blank=True, help_text="Dict with 'recommended' and 'avoid' lists")
    home_remedies = models.JSONField(default=list, blank=True, help_text="List of home remedies")
    specialist = models.CharField(max_length=255, help_text="Name of the specialist")

    class Meta:
        db_table = 'diseases'

    def __str__(self):
        return self.disease_name

class Medicine(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE, related_name='medicines')
    medicine_name = models.CharField(max_length=255)
    medicine_type = models.CharField(max_length=100, default='OTC') # 'OTC' or 'Prescription'
    otc = models.BooleanField(default=True)
    description = models.TextField()
    precautions = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'medicines'

    def __str__(self):
        return f"{self.medicine_name} ({self.medicine_type})"

class RecommendationHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recommendation_histories'
    )
    prediction = models.ForeignKey(
        'prediction.PredictionHistory',
        on_delete=models.CASCADE,
        related_name='recommendations',
        null=True,
        blank=True
    )
    disease = models.CharField(max_length=255)
    specialist = models.CharField(max_length=255)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'recommendation_history'
        ordering = ['-viewed_at']
        verbose_name_plural = "Recommendation Histories"

    def __str__(self):
        return f"Recommendation of {self.disease} for {self.user.username} at {self.viewed_at}"
