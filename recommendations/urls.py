from django.urls import path
from .views import (
    MedicinesMapsView, 
    RecommendationsAPIView, 
    GetRecommendationByDiseaseView
)
from hospitals.views import NearbyHospitalsAPIView

app_name = 'recommendations'

urlpatterns = [
    path('medicines-maps/', MedicinesMapsView.as_view(), name='medicines_maps'),
    path('api/recommendations', RecommendationsAPIView.as_view(), name='api_recommendations'),
    path('api/recommendations/disease', GetRecommendationByDiseaseView.as_view(), name='api_recommendations_by_disease'),
    path('api/hospitals', NearbyHospitalsAPIView.as_view(), name='api_hospitals'),
]
