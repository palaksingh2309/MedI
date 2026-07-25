import json
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from hospitals.services.hospital_service import HospitalService

@method_decorator(csrf_exempt, name='dispatch')
class NearbyHospitalsAPIView(View):
    """
    POST /api/hospitals
    Accepts latitude and longitude and returns a list of nearby hospitals/clinics.
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
                
            latitude = data.get("latitude")
            longitude = data.get("longitude")
            
            if latitude is None or longitude is None:
                return JsonResponse({"error": "Missing 'latitude' or 'longitude' field."}, status=400)
                
            try:
                lat = float(latitude)
                lon = float(longitude)
            except (ValueError, TypeError):
                return JsonResponse({"error": "Latitude and longitude must be valid float numbers."}, status=400)
                
            # Basic range check
            if not (-90.0 <= lat <= 90.0) or not (-180.0 <= lon <= 180.0):
                return JsonResponse({"error": "Latitude or longitude out of geographical range."}, status=400)
                
            hospitals = HospitalService.get_nearby_hospitals(lat, lon)
            return JsonResponse(hospitals, safe=False, status=200)
            
        except Exception as e:
            return JsonResponse({"error": f"Internal server error: {str(e)}"}, status=500)
