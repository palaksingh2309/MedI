from django.contrib import admin
from .models import Prediction, SavedClinic, ChatMessage, MedicalReport

@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ('predicted_disease', 'user', 'confidence_score', 'created_at')
    search_fields = ('predicted_disease', 'symptoms', 'user__username')
    list_filter = ('created_at',)

@admin.register(SavedClinic)
class SavedClinicAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'rating', 'created_at')
    search_fields = ('name', 'address', 'user__username')
    list_filter = ('rating', 'created_at')

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'created_at')
    search_fields = ('content', 'user__username', 'role')
    list_filter = ('role', 'created_at')

@admin.register(MedicalReport)
class MedicalReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'file', 'created_at')
    search_fields = ('summary', 'user__username')
    list_filter = ('created_at',)

