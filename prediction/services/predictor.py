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

        cls._is_loaded = True
        print(f"Prediction model assets loaded successfully! (Features: {len(cls._feature_columns)}, Classes: {len(cls._encoder.classes_)})")

    @classmethod
    def get_all_symptoms(cls):
        """
        Returns the list of valid symptom columns.
        """
        cls.load_assets()
        return cls._feature_columns

    @classmethod
    def predict(cls, user_symptoms):
        """
        Accepts a list of input symptoms (e.g., ["fever", "cough"]),
        normalizes them, validates against features, and predicts the disease.
        
        Returns:
            dict: Containing prediction, confidence, description, precautions,
                  and top 3 predictions for a richer UI experience.
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

        if not normalized_inputs:
            raise ValueError("Symptom list cannot be empty.")

        # 2. Validate symptoms against the model's feature columns
        invalid_symptoms = [s for s in normalized_inputs if s not in cls._feature_columns]
        if invalid_symptoms:
            raise ValueError(f"Unknown symptom(s): {', '.join(invalid_symptoms)}")

        # 3. Construct binary feature vector
        vector = np.zeros(len(cls._feature_columns))
        for s in normalized_inputs:
            index = cls._feature_columns.index(s)
            vector[index] = 1

        # Reshape for sklearn prediction (1 sample)
        vector = vector.reshape(1, -1)

        # 4. Predict probabilities
        probabilities = cls._model.predict_proba(vector)[0]
        
        # Get sorted predictions (descending order of probability)
        class_indices = np.argsort(probabilities)[::-1]

        # Best prediction
        best_index = class_indices[0]
        predicted_disease = cls._encoder.classes_[best_index]
        confidence_score = float(probabilities[best_index] * 100) # Represent as percentage

        # Top 3 predictions for rich UI
        top_predictions = []
        for idx in class_indices[:3]:
            disease_name = cls._encoder.classes_[idx]
            prob = float(probabilities[idx] * 100)
            top_predictions.append({
                "disease": disease_name,
                "confidence": round(prob, 2),
                "description": cls._descriptions.get(disease_name, "No description available."),
                "precautions": cls._precautions.get(disease_name, [])
            })

        # Fetch description and precautions for the primary prediction
        description = cls._descriptions.get(predicted_disease, "No description available.")
        precautions = cls._precautions.get(predicted_disease, [])

        return {
            "prediction": predicted_disease,
            "confidence": round(confidence_score, 2),
            "description": description,
            "precautions": precautions,
            "top_predictions": top_predictions,
            "model_version": "1.0.0" # Hardcoded or loaded from version config
        }
