import os
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

def main():
    print("Starting model evaluation...")
    
    # Paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    datasets_dir = os.path.join(base_dir, "datasets")
    models_dir = os.path.join(base_dir, "models")
    notebooks_dir = os.path.join(base_dir, "notebooks")
    
    path_symptoms = os.path.join(datasets_dir, "symptoms.csv")
    path_model = os.path.join(models_dir, "disease_model.pkl")
    path_encoder = os.path.join(models_dir, "encoder.pkl")
    path_features = os.path.join(models_dir, "feature_columns.pkl")
    
    if not (os.path.exists(path_symptoms) and os.path.exists(path_model) and os.path.exists(path_encoder)):
        raise FileNotFoundError("Model assets or dataset files are missing. Run preprocess.py and train.py first.")
    
    # Load assets
    df = pd.read_csv(path_symptoms)
    X = df.drop(columns=['disease'])
    y = df['disease']
    
    with open(path_model, "rb") as f:
        model = pickle.load(f)
    with open(path_encoder, "rb") as f:
        encoder = pickle.load(f)
        
    y_encoded = encoder.transform(y)
    
    # Split using same random state/ratio as train.py
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    # Predict
    y_pred = model.predict(X_test)
    
    # Accuracy
    acc = accuracy_score(y_test, y_pred)
    print(f"Test Set Accuracy: {acc * 100:.2f}%")
    
    # Classification Report
    print("\nClassification Report:")
    target_names = [str(c) for c in encoder.classes_]
    report = classification_report(y_test, y_pred, target_names=target_names)
    print(report)
    
    # Save classification report as a text file for records
    report_path = os.path.join(models_dir, "classification_report.txt")
    with open(report_path, "w") as f:
        f.write(report)
    print(f"Saved text classification report to {report_path}")
    
    # Confusion Matrix Plotting
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(18, 14))
    sns.heatmap(
        cm, 
        annot=True, 
        fmt="d", 
        cmap="Blues", 
        xticklabels=target_names, 
        yticklabels=target_names
    )
    plt.title("Confusion Matrix - Disease Prediction Model", fontsize=16)
    plt.ylabel("Actual Disease", fontsize=12)
    plt.xlabel("Predicted Disease", fontsize=12)
    plt.xticks(rotation=90)
    plt.yticks(rotation=0)
    plt.tight_layout()
    
    # Save plot
    os.makedirs(notebooks_dir, exist_ok=True)
    matrix_path = os.path.join(notebooks_dir, "confusion_matrix.png")
    plt.savefig(matrix_path, dpi=300)
    plt.close()
    print(f"Saved Confusion Matrix visualization to {matrix_path}")
    print("Evaluation completed successfully!")

if __name__ == "__main__":
    main()
