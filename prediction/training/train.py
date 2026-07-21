import os
import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score

def main():
    print("Starting model training pipeline...")
    
    # Paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    datasets_dir = os.path.join(base_dir, "datasets")
    models_dir = os.path.join(base_dir, "models")
    
    path_symptoms = os.path.join(datasets_dir, "symptoms.csv")
    
    if not os.path.exists(path_symptoms):
        raise FileNotFoundError(f"Cleaned dataset not found at {path_symptoms}. Run preprocess.py first.")
    
    os.makedirs(models_dir, exist_ok=True)
    
    # Load dataset
    df = pd.read_csv(path_symptoms)
    
    # Extract features and targets
    X = df.drop(columns=['disease'])
    y = df['disease']
    
    # 1. Save feature columns (crucial for inference order validation)
    feature_cols = list(X.columns)
    path_features = os.path.join(models_dir, "feature_columns.pkl")
    with open(path_features, "wb") as f:
        pickle.dump(feature_cols, f)
    print(f"Saved {len(feature_cols)} feature columns to {path_features}")
    
    # 2. Encode labels
    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(y)
    
    path_encoder = os.path.join(models_dir, "encoder.pkl")
    with open(path_encoder, "wb") as f:
        pickle.dump(encoder, f)
    print(f"Saved LabelEncoder (classes: {len(encoder.classes_)}) to {path_encoder}")
    
    # 3. Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    print(f"Dataset split: Train shape {X_train.shape}, Test shape {X_test.shape}")
    
    # 4. Compare multiple models
    models = {
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "Naive Bayes": GaussianNB(),
        "Random Forest (Default)": RandomForestClassifier(random_state=42)
    }
    
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        print(f"Model: {name} | Test Accuracy: {acc:.4f}")
    
    # 5. Hyperparameter Tuning on Random Forest
    print("\nTuning Random Forest using GridSearchCV...")
    rf = RandomForestClassifier(random_state=42)
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [10, 20, None],
        'min_samples_leaf': [1, 2, 4],
        'criterion': ['gini', 'entropy']
    }
    
    grid_search = GridSearchCV(
        estimator=rf,
        param_grid=param_grid,
        cv=3,
        scoring='accuracy',
        n_jobs=-1
    )
    grid_search.fit(X_train, y_train)
    
    best_rf = grid_search.best_estimator_
    best_params = grid_search.best_params_
    best_score = grid_search.best_score_
    
    print(f"Grid Search Best CV Accuracy: {best_score:.4f}")
    print(f"Best Parameters: {best_params}")
    
    # Evaluate best RF model on test set
    y_pred_best = best_rf.predict(X_test)
    test_acc_best = accuracy_score(y_test, y_pred_best)
    print(f"Best Random Forest Test Accuracy: {test_acc_best:.4f}")
    
    # 6. Save the selected best model (Random Forest)
    path_model = os.path.join(models_dir, "disease_model.pkl")
    with open(path_model, "wb") as f:
        pickle.dump(best_rf, f)
    print(f"Saved Best Random Forest model to {path_model}")
    print("Training pipeline completed!")

if __name__ == "__main__":
    main()
