import os
import pickle
import pandas as pd
import numpy as np
from django.conf import settings

class DiseasePredictor:
    _model = None
    _encoder = None
    _feature_columns = None
    _descriptions = {}
    _precautions = {}
    _disease_symptoms = {}
    _is_loaded = False

    @classmethod
    def load_assets(cls):
        """
        Loads the ML models and reference datasets in memory.
        This is designed to be thread-safe and cached.
        """
        if cls._is_loaded:
            return

        print("Loading prediction model assets into memory...")
        prediction_dir = os.path.join(settings.BASE_DIR, 'prediction')
        models_dir = os.path.join(prediction_dir, 'models')
        datasets_dir = os.path.join(prediction_dir, 'datasets')

        # Model file paths
        model_path = os.path.join(models_dir, 'disease_model.pkl')
        encoder_path = os.path.join(models_dir, 'encoder.pkl')
        features_path = os.path.join(models_dir, 'feature_columns.pkl')

        # Dataset file paths
        desc_path = os.path.join(datasets_dir, 'symptom_description.csv')
        prec_path = os.path.join(datasets_dir, 'symptom_precaution.csv')

        # Verify model files exist
        if not (os.path.exists(model_path) and os.path.exists(encoder_path) and os.path.exists(features_path)):
            raise FileNotFoundError(
                f"Model assets not found in {models_dir}. Run training scripts first."
            )

        # Load Pickle assets
        with open(model_path, 'rb') as f:
            cls._model = pickle.load(f)
        with open(encoder_path, 'rb') as f:
            cls._encoder = pickle.load(f)
        with open(features_path, 'rb') as f:
            cls._feature_columns = pickle.load(f)

        # Load Descriptions dataset if available
        if os.path.exists(desc_path):
            try:
                df_desc = pd.read_csv(desc_path)
                cls._descriptions = dict(zip(df_desc['disease'], df_desc['description']))
            except Exception as e:
                print(f"Error loading descriptions: {e}")

        # Load Precautions dataset if available
        if os.path.exists(prec_path):
            try:
                df_prec = pd.read_csv(prec_path)
                for _, row in df_prec.iterrows():
                    disease = row['disease']
                    # Extract precaution columns that are not empty
                    prec_list = [row[col] for col in df_prec.columns if col.startswith('precaution_') and pd.notna(row[col]) and str(row[col]).strip() != '']
                    cls._precautions[disease] = prec_list
            except Exception as e:
                print(f"Error loading precautions: {e}")

        # Load standard symptoms per disease from symptoms.csv
        symptoms_csv_path = os.path.join(datasets_dir, 'symptoms.csv')
        if os.path.exists(symptoms_csv_path):
            try:
                df_sym = pd.read_csv(symptoms_csv_path)
                cls._disease_symptoms = {}
                for disease in df_sym['disease'].unique():
                    sub_df = df_sym[df_sym['disease'] == disease].drop(columns=['disease'])
                    # Find all columns where the sum is greater than 0
                    active_cols = sub_df.columns[sub_df.sum() > 0].tolist()
                    cls._disease_symptoms[disease] = active_cols
            except Exception as e:
                print(f"Error extracting active symptoms per disease: {e}")

        cls._is_loaded = True
        print(f"Prediction model assets loaded successfully! (Features: {len(cls._feature_columns)}, Classes: {len(cls._encoder.classes_)})")

    @classmethod
    def get_all_symptoms(cls):
        """
        Returns the list of valid symptom columns.
        """
        cls.load_assets()
        return cls._feature_columns

    _generic_symptoms = {
        "high_fever", "mild_fever", "headache", "nausea", 
        "fatigue", "stomach_pain", "abdominal_pain", 
        "acidity", "indigestion", "vomiting"
    }

    _rare_diseases = {
        "AIDS", "Paralysis (brain hemorrhage)", "Drug Reaction", "Chronic cholestasis"
    }

    @classmethod
    def _get_symptom_weight(cls, symptom):
        return 0.2 if symptom in cls._generic_symptoms else 1.0

    @classmethod
    def _generate_follow_up_questions(cls, user_symptoms):
        """
        Dynamically finds symptoms that co-occur with the user's current symptoms
        in the typical symptoms list of matching diseases, and builds user-friendly questions.
        """
        associated_diseases = []
        user_symptoms_set = set(user_symptoms)
        
        for disease, symptoms in cls._disease_symptoms.items():
            if user_symptoms_set.intersection(symptoms):
                associated_diseases.append(disease)
                
        if not associated_diseases:
            # If no direct matches, default to all diseases
            associated_diseases = list(cls._disease_symptoms.keys())
            
        candidate_symptoms = []
        for disease in associated_diseases:
            candidate_symptoms.extend(cls._disease_symptoms[disease])
            
        # Filter out user's existing symptoms and unknown symptoms
        candidate_symptoms = [
            s for s in candidate_symptoms 
            if s not in user_symptoms_set and s in cls._feature_columns
        ]
        
        from collections import Counter
        counts = Counter(candidate_symptoms)
        
        # Get the top 4 most frequent co-occurring symptoms
        top_candidates = [s for s, _ in counts.most_common(4)]
        
        questions = []
        for sym in top_candidates:
            clean_name = sym.replace("_", " ").strip()
            if "pain" in clean_name:
                text = f"Are you experiencing any {clean_name}?"
            elif clean_name.endswith("s") or "spots" in clean_name or "patches" in clean_name:
                text = f"Have you noticed any {clean_name}?"
            else:
                text = f"Are you experiencing {clean_name}?"
            questions.append({
                "symptom": sym,
                "question": text
            })
        return questions

    @classmethod
    def predict(cls, user_symptoms, severity="mild", duration=1):
        """
        Accepts a list of input symptoms (e.g., ["fever", "cough"]),
        normalizes them, validates against features, and predicts the disease.
        
        Returns:
            dict: Containing structured JSON output.
        """
        cls.load_assets()

        # 1. Normalize input symptoms: lowercase, strip, and replace spaces with underscores
        normalized_inputs = []
        for s in user_symptoms:
            cleaned = str(s).strip().lower().replace(" ", "_")
            if cleaned:
                normalized_inputs.append(cleaned)

        # Remove duplicate input symptoms
        normalized_inputs = list(set(normalized_inputs))

        # Check for empty inputs
        if not normalized_inputs:
            raise ValueError("Symptom list cannot be empty.")

        # 2. Validate symptoms against the model's feature columns
        invalid_symptoms = [s for s in normalized_inputs if s not in cls._feature_columns]
        if invalid_symptoms:
            raise ValueError(f"Unknown symptom(s): {', '.join(invalid_symptoms)}")

        # 3. Determine severity and duration logic
        emergency_warning = None
        recommendation = ""
        
        try:
            duration_days = int(duration)
        except (ValueError, TypeError):
            duration_days = 1

        if severity == "severe":
            emergency_warning = "Severe symptoms detected. Please consult a healthcare professional immediately or visit the nearest emergency department."
            recommendation = "Given the high severity of your symptoms, we strongly recommend seeking an immediate medical consultation."
        elif duration_days >= 7:
            recommendation = "Your symptoms have persisted for a week or longer. We advise consulting a healthcare professional for a comprehensive evaluation."
        elif severity == "mild":
            recommendation = "Your symptoms appear mild and of short duration. Home care, rest, and hydration are suggested. Monitor your condition, and consult a doctor if symptoms worsen."
        else: # moderate
            recommendation = "You are experiencing moderate symptoms. We suggest monitoring your health closely. If symptoms worsen or persist for more than a few days, please schedule a medical consultation."

        # 4. Check for rule-based blocks
        blocked_diseases = set()
        symptom_set = set(normalized_inputs)
        if "stomach_pain" in symptom_set and len(symptom_set) == 1:
            blocked_diseases.add("Drug Reaction")
        if ("high_fever" in symptom_set or "mild_fever" in symptom_set) and len(symptom_set) == 1:
            blocked_diseases.add("AIDS")
        if "headache" in symptom_set and len(symptom_set) == 1:
            blocked_diseases.add("Paralysis (brain hemorrhage)")

        # 5. Check symptom sufficiency
        if len(normalized_inputs) < 3:
            return {
                "sufficientSymptoms": False,
                "prediction": None,
                "confidence": 0.0,
                "predictionConfidence": None,
                "top_predictions": [],
                "topPredictions": [],
                "followUpQuestions": cls._generate_follow_up_questions(normalized_inputs),
                "recommendation": recommendation,
                "emergencyWarning": emergency_warning,
                "description": None,
                "precautions": [],
                "warning": "Fewer than 3 symptoms provided. Please answer follow-up questions to help narrow down the diagnosis.",
                "model_version": "1.0.0"
            }

        # 6. Construct binary feature vector
        vector = np.zeros(len(cls._feature_columns))
        for s in normalized_inputs:
            index = cls._feature_columns.index(s)
            vector[index] = 1

        # Reshape for sklearn prediction (1 sample)
        vector = vector.reshape(1, -1)

        # 7. Predict probabilities
        probabilities = cls._model.predict_proba(vector)[0]
        
        # Check if all symptoms are generic
        all_generic = all(s in cls._generic_symptoms for s in normalized_inputs)
        
        # Calculate adjusted confidence scores for all classes
        adjusted_predictions = []
        for idx, raw_prob in enumerate(probabilities):
            disease_name = cls._encoder.classes_[idx]
            
            # Apply rule-based check blocks
            if disease_name in blocked_diseases:
                raw_prob = 0.0
                
            # Prioritize common illnesses over extremely rare diseases when symptoms are generic
            if all_generic and disease_name in cls._rare_diseases:
                raw_prob = raw_prob * 0.05
                
            raw_percent = float(raw_prob * 100)
            
            # calculate weighted overlap ratio
            matched_weight = 0.0
            total_weight = 1.0
            overlap_ratio = 1.0
            
            if disease_name in cls._disease_symptoms:
                standard_symptoms = cls._disease_symptoms[disease_name]
                matched_symptoms = set(normalized_inputs).intersection(standard_symptoms)
                matched_weight = sum(cls._get_symptom_weight(s) for s in matched_symptoms)
                total_weight = sum(cls._get_symptom_weight(s) for s in standard_symptoms)
                if total_weight > 0:
                    overlap_ratio = matched_weight / total_weight
            
            # Scale down the confidence
            adjusted_percent = raw_percent * overlap_ratio
            
            adjusted_predictions.append({
                "idx": idx,
                "disease": disease_name,
                "raw_confidence": raw_percent,
                "confidence": adjusted_percent,
                "overlap_ratio": overlap_ratio,
                "symptom_match": f"{len(matched_symptoms)}/{len(standard_symptoms)}"
            })
            
        # Re-sort predictions in descending order of adjusted confidence
        adjusted_predictions.sort(key=lambda x: (x["confidence"], x["raw_confidence"]), reverse=True)
        
        # Top 3 predictions
        top_3_predictions = []
        for pred in adjusted_predictions[:3]:
            disease_name = pred["disease"]
            top_3_predictions.append({
                "disease": disease_name,
                "confidence": round(pred["confidence"], 2),
                "description": cls._descriptions.get(disease_name, "No description available."),
                "precautions": cls._precautions.get(disease_name, []),
                "raw_confidence": round(pred["raw_confidence"], 2),
                "symptom_match": pred["symptom_match"]
            })
            
        # Best prediction
        best_prediction = adjusted_predictions[0]
        confidence_score = best_prediction["confidence"]
        predicted_disease = best_prediction["disease"]
        
        # Enforce 75% confidence threshold for definitive prediction
        has_definitive = confidence_score > 75.0
        final_prediction = predicted_disease if has_definitive else None
        final_confidence = round(confidence_score, 2) if has_definitive else None
        
        # Warning message if confidence is low
        warning_msg = None
        if not has_definitive:
            warning_msg = "Symptom overlap is high across many conditions. Showing likely possible conditions instead of a definitive diagnosis."
            
        description = cls._descriptions.get(predicted_disease, "No description available.") if has_definitive else "Symptoms overlap across many illnesses. A single definitive diagnosis cannot be made with confidence."
        precautions = cls._precautions.get(predicted_disease, []) if has_definitive else []

        return {
            "sufficientSymptoms": True,
            "prediction": final_prediction,
            "confidence": round(confidence_score, 2), # for compatibility
            "predictionConfidence": final_confidence,
            "description": description,
            "precautions": precautions,
            "top_predictions": top_3_predictions, # compatibility
            "topPredictions": top_3_predictions,
            "followUpQuestions": [],
            "recommendation": recommendation,
            "emergencyWarning": emergency_warning,
            "warning": warning_msg,
            "model_version": "1.0.0"
        }
