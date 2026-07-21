from django.db import models
from django.conf import settings

class PredictionHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='prediction_histories'
    )
    symptoms = models.JSONField(help_text="JSON list of symptoms input by the user")
    prediction = models.CharField(max_length=255, help_text="Predicted disease name")
    confidence = models.FloatField(help_text="Confidence score of the prediction (percentage)")
    model_version = models.CharField(max_length=50, default="1.0.0", help_text="Version of the model used")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'prediction_history'
        verbose_name_plural = "Prediction Histories"
        ordering = ['-created_at']

    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"{self.prediction} ({self.confidence:.1f}%) for {username} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"
