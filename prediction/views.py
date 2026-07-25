import json
import time
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
import logging

from .services.predictor import DiseasePredictor
from .models import PredictionHistory
from .utils import rate_limit, log_prediction

# User model
User = get_user_model()

@method_decorator(csrf_exempt, name='dispatch')
class PredictView(View):
    """
    POST /api/predict
    Inferences the disease prediction model using the user's provided symptoms.
    """
    @method_decorator(rate_limit(key_prefix="predict_api", limit=20, period=60))
    def post(self, request, *args, **kwargs):
        # 1. Enforce authentication
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required. Please login."}, status=401)

        start_time = time.time()
        
        try:
            # 2. Parse payload
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON format in request body."}, status=400)

            symptoms = data.get("symptoms")
            severity = str(data.get("severity", "mild")).strip().lower()
            if severity not in ("mild", "moderate", "severe"):
                severity = "mild"
                
            try:
                duration = int(data.get("duration", 1))
            except (ValueError, TypeError):
                duration = 1
            
            # 3. Payload validation
            if symptoms is None:
                return JsonResponse({"error": "Missing 'symptoms' field in request body."}, status=400)

            if not isinstance(symptoms, list):
                return JsonResponse({"error": "'symptoms' must be a list of strings."}, status=400)

            # Clean/strip whitespace
            symptoms = [str(s).strip() for s in symptoms if str(s).strip()]

            if not symptoms:
                return JsonResponse({"error": "Symptoms list cannot be empty."}, status=400)

            if len(symptoms) > 15:
                return JsonResponse({"error": "Too many symptoms. Maximum allowed is 15."}, status=400)

            # 4. Predict
            try:
                result = DiseasePredictor.predict(symptoms, severity=severity, duration=duration)
            except ValueError as val_err:
                # Catch unknown symptoms or validation errors from predictor
                return JsonResponse({"error": str(val_err)}, status=400)

            # Calculate latency in milliseconds
            latency_ms = (time.time() - start_time) * 1000

            # 5. Persist Prediction History (only if sufficient symptoms are provided)
            prediction_id = None
            if result.get("sufficientSymptoms", True):
                hist_prediction = result["prediction"]
                hist_confidence = result["predictionConfidence"]
                
                if hist_prediction is None and result.get("topPredictions"):
                    hist_prediction = f"Possible: {result['topPredictions'][0]['disease']}"
                    hist_confidence = result['topPredictions'][0]['confidence']
                elif hist_prediction is None:
                    hist_prediction = "Undetermined"
                    hist_confidence = 0.0
                    
                prediction_record = PredictionHistory.objects.create(
                    user=request.user,
                    symptoms=symptoms,
                    prediction=hist_prediction,
                    confidence=hist_confidence,
                    model_version=result["model_version"]
                )
                prediction_id = str(prediction_record.id)

                # 6. Log prediction metrics
                log_prediction(
                    user=request.user,
                    disease=hist_prediction,
                    confidence=hist_confidence,
                    latency_ms=latency_ms
                )

            # Return success response
            return JsonResponse({
                "sufficientSymptoms": result["sufficientSymptoms"],
                "prediction": result["prediction"],
                "confidence": result["confidence"],
                "predictionConfidence": result["predictionConfidence"],
                "prediction_id": prediction_id,
                "description": result["description"],
                "precautions": result["precautions"],
                "topPredictions": result["topPredictions"],
                "top_predictions": result["top_predictions"],
                "followUpQuestions": result["followUpQuestions"],
                "recommendation": result["recommendation"],
                "emergencyWarning": result["emergencyWarning"],
                "warning": result.get("warning"),
                "latency_ms": round(latency_ms, 2)
            }, status=200)

        except Exception as e:
            # Prevent stack traces from escaping in production
            logger_err = logging.getLogger('prediction')
            logger_err.exception(f"Unhandled exception during prediction: {e}")
            return JsonResponse({"error": "Prediction service unavailable"}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class PredictionHistoryView(View):
    """
    GET /api/history
    Fetches the prediction history for the authenticated user.
    """
    def get(self, request, *args, **kwargs):
        # 1. Enforce authentication
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required. Please login."}, status=401)

        try:
            # Fetch prediction records for the current user
            records = PredictionHistory.objects.filter(user=request.user).order_by('-created_at')
            
            history_data = []
            for record in records:
                history_data.append({
                    "id": record.id,
                    "prediction": record.prediction,
                    "confidence": record.confidence,
                    "symptoms": record.symptoms,
                    "model_version": record.model_version,
                    "created_at": record.created_at.isoformat()
                })

            return JsonResponse(history_data, safe=False, status=200)

        except Exception as e:
            logger_err = logging.getLogger('prediction')
            logger_err.exception(f"Unhandled exception fetching history: {e}")
            return JsonResponse({"error": "Unable to fetch prediction history"}, status=500)


class PredictPageView(LoginRequiredMixin, TemplateView):
    template_name = 'prediction/predict.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            raw_symptoms = DiseasePredictor.get_all_symptoms()
            context['symptoms'] = [
                {"value": sym, "label": sym.replace('_', ' ').title()}
                for sym in raw_symptoms
            ]
        except Exception:
            context['symptoms'] = []
            
        context['recent_predictions'] = PredictionHistory.objects.filter(
            user=self.request.user
        ).order_by('-created_at')[:10]
        
        return context


class SymptomsListView(View):
    """
    GET /api/symptoms
    Returns list of all valid symptom strings supported by the ML model.
    """
    def get(self, request, *args, **kwargs):
        try:
            symptoms = DiseasePredictor.get_all_symptoms()
            symptom_list = [
                {"value": sym, "label": sym.replace('_', ' ').title()}
                for sym in symptoms
            ]
            return JsonResponse(symptom_list, safe=False, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
