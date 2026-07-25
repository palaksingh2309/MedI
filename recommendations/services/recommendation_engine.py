import logging
from recommendations.models import Disease, Medicine, Specialist

logger = logging.getLogger(__name__)

class RecommendationEngine:
    @staticmethod
    def get_recommendations(disease_name):
        """
        Retrieves medical recommendations (diet, precautions, home remedies, specialist, OTC medicines)
        from the database for a given disease name.
        """
        # Clean disease name: replace underscores with spaces and title-case it to match seeding
        cleaned_name = str(disease_name).strip()
        
        try:
            # Query the Disease model
            disease = Disease.objects.get(disease_name__iexact=cleaned_name)
        except Disease.DoesNotExist:
            # Try to query with prefix/partial if direct match fails
            try:
                disease = Disease.objects.filter(disease_name__icontains=cleaned_name).first()
                if not disease:
                    return None
            except Exception as e:
                logger.error(f"Error querying disease model: {e}")
                return None
                
        # Query associated medicines
        medicines_qs = Medicine.objects.filter(disease=disease, otc=True)
        medicines = []
        for med in medicines_qs:
            medicines.append({
                "medicine_name": med.medicine_name,
                "medicine_type": med.medicine_type,
                "otc": med.otc,
                "description": med.description,
                "precautions": med.precautions
            })
            
        # Get specialist description if available
        specialist_desc = ""
        try:
            spec = Specialist.objects.filter(specialist__iexact=disease.specialist).first()
            if spec:
                specialist_desc = spec.description
        except Exception:
            pass

        # Build response payload
        return {
            "disease": disease.disease_name,
            "description": disease.description,
            "specialist": disease.specialist,
            "specialist_description": specialist_desc,
            "precautions": disease.precautions,
            "diet": disease.diet, # dict with 'recommended' and 'avoid'
            "home_remedies": disease.home_remedies,
            "medicines": medicines,
            "prescription_warning": "" if medicines else "Prescription treatment required. Please consult a physician immediately."
        }
