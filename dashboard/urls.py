from django.urls import path
from .views import DashboardView
from prediction.views import PredictPageView

app_name = 'dashboard'

urlpatterns = [
    path('', DashboardView.as_view(), name='index'),
    path('predict/', PredictPageView.as_view(), name='predict_page'),
]
