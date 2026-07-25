import json
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from prediction.models import PredictionHistory
from recommendations.models import Disease, RecommendationHistory
from recommendations.services.recommendation_engine import RecommendationEngine

@method_decorator(csrf_exempt, name='dispatch')
class RecommendationsAPIView(View):
    """
    POST /api/recommendations
    Accepts prediction_id and returns medical recommendation details.
    Also logs the recommendation view to history.
    """
    def post(self, request, *args, **kwargs):
        # Enforce authentication
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required. Please login."}, status=401)
            
        try:
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON format in request body."}, status=400)
                
            prediction_id = data.get("prediction_id")
            if not prediction_id:
                return JsonResponse({"error": "Missing 'prediction_id' field in request body."}, status=400)
                
            try:
                prediction = PredictionHistory.objects.get(id=prediction_id, user=request.user)
            except PredictionHistory.DoesNotExist:
                return JsonResponse({"error": "Prediction record not found or access denied."}, status=404)
                
            # Get disease name (strip prefix if any)
            disease_name = prediction.prediction
            if not disease_name or disease_name == "Undetermined":
                return JsonResponse({"error": "No definitive prediction was made for this history record."}, status=400)
                
            if disease_name.startswith("Possible: "):
                disease_name = disease_name.replace("Possible: ", "")
                
            recommendation_data = RecommendationEngine.get_recommendations(disease_name)
            
            if not recommendation_data:
                return JsonResponse({"error": f"No recommendation data found for disease '{disease_name}'."}, status=404)
                
            # Save recommendation history record
            RecommendationHistory.objects.create(
                user=request.user,
                prediction=prediction,
                disease=recommendation_data["disease"],
                specialist=recommendation_data["specialist"]
            )
            
            return JsonResponse(recommendation_data, status=200)
            
        except Exception as e:
            return JsonResponse({"error": f"Internal server error: {str(e)}"}, status=500)


class MedicinesMapsView(LoginRequiredMixin, TemplateView):
    """
    GET /medicines-maps/
    Renders standalone search interface for clinics, maps, and medicines.
    """
    template_name = 'recommendations/medicines_maps.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch all diseases for the dropdown knowledge base
        context['diseases'] = Disease.objects.all().order_by('disease_name')
        
        # Add recommendation history to display in sidebar
        context['recent_recommendations'] = RecommendationHistory.objects.filter(
            user=self.request.user
        ).order_by('-viewed_at')[:10]
        
        return context


@method_decorator(csrf_exempt, name='dispatch')
class GetRecommendationByDiseaseView(View):
    """
    POST /api/recommendations/disease
    Helper endpoint for the standalone page. Looks up recommendations directly by disease name.
    """
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required. Please login."}, status=401)
            
        try:
            data = json.loads(request.body)
            disease_name = data.get("disease_name")
            if not disease_name:
                return JsonResponse({"error": "Missing 'disease_name' field."}, status=400)
                
            recommendation_data = RecommendationEngine.get_recommendations(disease_name)
            if not recommendation_data:
                return JsonResponse({"error": f"No recommendation data found for disease '{disease_name}'."}, status=404)
                
            # Save recommendation history (without prediction reference)
            RecommendationHistory.objects.create(
                user=request.user,
                prediction=None,
                disease=recommendation_data["disease"],
                specialist=recommendation_data["specialist"]
            )
            
            return JsonResponse(recommendation_data, status=200)
            
        except Exception as e:
            return JsonResponse({"error": f"Internal server error: {str(e)}"}, status=500)
