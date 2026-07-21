from django.urls import path
from .views import PredictView, PredictionHistoryView, SymptomsListView

app_name = 'prediction'

urlpatterns = [
    path('predict', PredictView.as_view(), name='predict'),
    path('history', PredictionHistoryView.as_view(), name='history'),
    path('symptoms', SymptomsListView.as_view(), name='symptoms_list'),
]
