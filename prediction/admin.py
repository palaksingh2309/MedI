from django.contrib import admin
from .models import PredictionHistory

@admin.register(PredictionHistory)
class PredictionHistoryAdmin(admin.ModelAdmin):
    list_display = ('prediction', 'user', 'confidence', 'model_version', 'created_at')
    search_fields = ('prediction', 'user__username', 'symptoms')
    list_filter = ('model_version', 'created_at')
    readonly_fields = ('created_at',)
