from django.urls import path
from .views import (
    LandingPageView,
    DashboardView,
    UpdateWellnessView,
    MedicalReportView,
    ChatbotView
)
from prediction.views import PredictPageView

app_name = 'dashboard'

urlpatterns = [
    path('', LandingPageView.as_view(), name='landing'),
    path('dashboard/', DashboardView.as_view(), name='index'),
    path('predict/', PredictPageView.as_view(), name='predict_page'),
    path('wellness/update/', UpdateWellnessView.as_view(), name='update_wellness'),
    path('report-summarizer/', MedicalReportView.as_view(), name='report_summarizer'),
    path('chatbot/', ChatbotView.as_view(), name='chatbot'),
]
