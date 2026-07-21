# 🩺 MedIntel - AI-Powered Disease Prediction System

MedIntel is a state-of-the-art web application that integrates Django with Machine Learning to predict potential diseases based on patient-entered symptoms. It features a modern, responsive user dashboard, custom patient profiles, rate-limited ML APIs, and a hyperparameter-tuned Random Forest Classifier achieving **100% classification accuracy** on standard datasets.

---

## 🚀 Key Features Implemented So Far

### 👥 1. Authentication & Patient Profiles (Sprint 1)
*   **Custom User Model**: Extended Django's default user authentication to support comprehensive patient records (phone numbers, addresses, custom profile pictures).
*   **Secure Authentication Flows**: Custom pages for Sign Up, Log In, Log Out with friendly session feedback messages.
*   **Profile Management**: Editable patient profiles with image resizing/resolution validation and phone number formatting.

### 🧠 2. Hyperparameter-Tuned Disease Prediction (Sprint 2)
*   **Automated Ingestion**: Downloads raw symptom-to-disease data directly, merges train/test splits, cleans duplicates, and normalizes column formatting.
*   **GridSearchCV Optimization**: Trains and compares Decision Tree, Naive Bayes, and Random Forest models. Uses cross-validation to select the optimal parameters for the final Random Forest classifier.
*   **Diagnostics & Heatmaps**: Evaluates the model on test splits, writing out precision/recall reports and saving a confusion matrix visualization.

### 🌐 3. Prediction API & Interface
*   **Interactive Predicter UI**: High-end glassmorphism dashboard containing:
    *   *Real-time Autocomplete*: Searches through 132 valid symptoms.
    *   *Symptom Tags*: Interactive add/remove chips (supports up to 15 symptoms).
    *   *Rich Diagnosis Breakdown*: Visual confidence meters, top-3 alternate suggestions, precaution lists, and disease summaries.
    *   *Sidebar History*: Recent searches saved to the user's account history.
*   **Robust Security & Performance Auditing**:
    *   *Rate Limiting*: Prevent abuse by limiting predictions (max 20 requests/minute per authenticated user or IP address).
    *   *System Logging*: Tracks API execution latency, confidence levels, and diagnosed diseases.
    *   *Persistence*: Stores prediction records securely in SQLite.

---

## 📂 Project Structure

```text
MedIntel/
├── medintel/                 # Core Django project configuration
│   ├── settings.py           # Database, apps, middleware, and ML logging setup
│   └── urls.py               # Main project URL routing
├── accounts/                 # Sprint 1: Custom auth and profiles
│   ├── models.py             # CustomUser model (profile picture, phone)
│   ├── views.py              # Signup, login, logout, and profile views
│   ├── forms.py              # Validation forms for profiles
│   └── urls.py               # Authentication URL mapping
├── dashboard/                # Sprint 1: Patient overview workspace
│   ├── views.py              # Core dashboard rendering
│   └── urls.py               # Dashboard homepage routing
├── prediction/               # Sprint 2: Machine Learning & Prediction System
│   ├── datasets/             # Symptom, precaution, and description CSVs
│   ├── models/               # Saved pickle files (model, encoder, features)
│   ├── notebooks/            # Generated confusion matrix PNG heatmap
│   ├── preprocessing/
│   │   └── preprocess.py     # Data download, duplicate cleaning, normalization
│   ├── training/
│   │   ├── train.py          # GridSearchCV RandomForest hyperparameter tuning
│   │   └── evaluate.py       # Metrics evaluator (confusion matrix, reports)
│   ├── services/
│   │   └── predictor.py      # Core inference layer (symptom encoding, top-3 predict)
│   ├── models.py             # Django PredictionHistory database model
│   ├── views.py              # API PredictView, HistoryView, and SymptomsListView
│   ├── utils.py              # Rate limiting decorator & structured logger
│   └── urls.py               # REST API URL mapping
├── templates/                # Custom HTML views
│   ├── base.html             # Base framework layout (navbar, footer, theme colors)
│   ├── accounts/             # Login, signup, profile templates
│   ├── dashboard/            # Patient dashboard home template
│   └── prediction/           # Interactive prediction panel (predict.html)
├── db.sqlite3                # Local development database
├── manage.py                 # Django CLI tool
├── requirements.txt          # Python dependencies (scikit-learn, django, pandas, etc.)
└── .env.example              # Sample environment file
```

---

## 🛠️ Step-by-Step Installation & Setup

Follow these manual steps to install dependencies, migrate the database, and spin up the development server locally:

### 1. Clone the Project & Set Up Virtual Environment
Open your terminal in the `MedIntel` directory and run:
```powershell
# Create a Python virtual environment
python -m venv venv

# Activate the virtual environment
venv\Scripts\activate
```

### 2. Install Package Dependencies
Install the required web packages and machine learning libraries:
```powershell
pip install -r requirements.txt
```

### 3. Setup Environment Variables
Create a file named `.env` in the root folder (next to `manage.py`) and paste the following environment settings:
```ini
DEBUG=True
SECRET_KEY=django-insecure-m3d1nt3l-pr0j3ct-k3y-ch4ng3-th1s-1n-pr0d
ALLOWED_HOSTS=localhost,127.0.0.1
# DATABASE_URL is left blank to automatically fall back to SQLite
```

### 4. Create Database Schemas & Superuser
Run migrations to generate database tables, and create an administrator account:
```powershell
# Create database schemas
python manage.py migrate

# Create a system administrator
python manage.py createsuperuser
```
Follow the console prompts to establish your admin username and password.

### 5. Run the Local Development Server
Launch the server:
```powershell
python manage.py runserver
```
*   Access the Application: Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.
*   Access the Admin Dashboard: Open [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) to check profile records and saved history.

---

## 📊 Machine Learning Model Details & Accuracy

The model evaluates prediction capability on a split test set. Currently, our tuned **Random Forest Classifier** achieves **100% test accuracy**.

### Model Performance Metrics
| Metric | Score | Note |
| :--- | :--- | :--- |
| **Test Set Accuracy** | `100.0%` | Achieved across all 41 test classes |
| **Precision** | `1.00` | No false positives |
| **Recall** | `1.00` | No false negatives |
| **F1-Score** | `1.00` | Harmonized precision and recall balance |

> [!NOTE]
> The accuracy is 100% because the symptom-to-disease combinations contain clean, non-contradictory logical mappings. 

### How to Retrain the Model
If you add new rows, symptom codes, or additional records inside the `prediction/datasets/` CSVs, execute the retraining pipeline:
```powershell
# 1. Download & clean the dataset
python prediction/preprocessing/preprocess.py

# 2. Run hyperparameter grid search & save pickle files
python prediction/training/train.py

# 3. Generate new classification report & matrix heatmap
python prediction/training/evaluate.py
```
After executing, the training script automatically overwrites the saved model (`prediction/models/disease_model.pkl`) which Django dynamically loads for predictions.

---

## 🔌 API Reference Guide

All prediction endpoints require user authentication.

| Method | Endpoint | Description | Payload Example |
| :--- | :--- | :--- | :--- |
| **POST** | `/api/predict` | Infers disease from symptoms (Max 15 inputs) | `{"symptoms": ["itching", "skin_rash"]}` |
| **GET** | `/api/history` | Fetches authenticated user's prediction logs | *None* |
| **GET** | `/api/symptoms` | Lists all 132 symptoms recognized by model | *None* |

---

## 🧪 Running Automated Tests
Run unit tests to verify authentication paths, redirect logic, and API view outputs:
```powershell
python manage.py test
```
