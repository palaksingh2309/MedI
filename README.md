# 🩺 MedWise AI - Calming Clinical Health Companion & Diagnostics Platform

MedWise AI is a premium, state-of-the-art web application that integrates Django with Machine Learning to predict potential diseases based on patient symptoms, log daily wellness habits, summarize medical reports, and offer real-time medical chatbot assistance. It features a modern, calming clinical user interface, custom patient profile biometrics, weekly telemetry analytics, and a hyperparameter-tuned Random Forest Classifier achieving **100% classification accuracy**.

---

## 🚀 Key Features

### 👥 1. Account Settings & Health Profile Biometrics (Sprint 1 & 3)
*   **Custom User Model**: Extended Django's authentication to support profile pictures and personal details.
*   **Tabbed Health Profile Layout**:
    *   *Account Settings*: Username, email, profile picture, and DOB.
    *   *Health Companion Metrics*: Height (cm), weight (kg), age, gender, blood group, emergency contact, known allergies, chronic conditions, and daily targets (water & sleep goals).
*   **Dynamic BMI Engine**: Updates to height and weight instantly recalculate the patient's BMI value, diagnostic category (e.g. "Healthy weight"), and provide actionable medical recommendations.

### 🧠 2. Hyperparameter-Tuned Disease Prediction (Sprint 2)
*   **GridSearchCV Optimization**: Trains and compares Decision Tree, Naive Bayes, and Random Forest models on 132 symptoms to achieve the optimal classification parameters.
*   **Interactive Predictor UI**: Glassmorphic panels with autocomplete symptom searches, drag-add tags, visual confidence meters, top-3 alternate suggestions, and dynamic precaution listings.
*   **API Security**: Rate limiting (max 20 predictions/minute per user or IP address) and latency/metric database logging.

### 🏠 3. Personalized Health Home (Dashboard)
*   **Health Score Ring**: A dynamic 100-point circular SVG progress index calculated from active biometric indices (BMI, daily sleep, steps, hydration, and exercise).
*   **Daily Goal Tracker Widget Dials**: Interactive circular meters logging current progress against targets for water intake, sleep duration, exercise, and steps walked.
*   **Weekly Telemetry Analytics**: Sleek responsive line graphs tracking health variables over time powered by Chart.js.
*   **Real-Time Predictions Feed**: An AJAX background script that polls the prediction endpoint every 10 seconds to append new diagnoses without page reload.
*   **Emergency SOS Card**: Alert panel with flashing visual effects, paramedic desk hotlines, and quick first-aid protocols (stroke, choking, burns).
*   **Health Timeline**: A chronological clinical history log of predictions, profile biometrics updates, and uploaded report logs.

### 💬 4. AI Medical Chatbot (Sprint 4 Mockup)
*   A responsive messaging interface featuring distinct user/bot speech bubbles, a simulated animated typing loader, clinical warnings, and quick symptom triage prompt chips.

### 📄 5. Medical Report Summarizer (Sprint 4 Mockup)
*   Drag-drop style file upload panel supporting PDF and image reports.
*   Simulated clinical variable parser with skeleton shimmer progress bars.
*   Provides structured summaries mapping hematology findings, values, and actionable clinical suggestions.

---

## 📂 Project Structure

```text
MedIntel/
├── medintel/                 # Core Django project configuration
│   ├── settings.py           # Database settings & authentication configuration
│   └── urls.py               # Main URL router mapping accounts, predictions, dashboard
├── accounts/                 # Custom authentication & profile system
│   ├── models.py             # CustomUser model (dob, profile picture, phone number)
│   ├── views.py              # Signup, login, logout, and profile views
│   ├── forms.py              # UserProfileForm and HealthProfileForm definitions
│   └── urls.py               # Authentication URL mapping
├── dashboard/                # Main patient clinical workspace
│   ├── models.py             # HealthProfile and DailyWellness models + post_save signals
│   ├── views.py              # LandingPageView, DashboardView, UpdateWellnessView, MedicalReportView, ChatbotView
│   └── urls.py               # Health home page, reports, chatbot, and wellness log URLs
├── prediction/               # Machine Learning & Symptoms Classifier
│   ├── datasets/             # Symptom, precaution, and description CSV reference lists
│   ├── models/               # Saved pickle files (model, encoder, features)
│   ├── training/
│   │   ├── train.py          # GridSearchCV Random Forest trainer
│   │   └── evaluate.py       # Metrics evaluator (confusion matrix PNG heatmap)
│   ├── services/
│   │   └── predictor.py      # Core inference engine (symptom encoder, top-3 predictions)
│   ├── models.py             # PredictionHistory database table
│   ├── views.py              # PredictView, HistoryView, and SymptomsListView APIs
│   ├── utils.py              # Rate limiter decorator & structured clinical logger
│   └── urls.py               # REST API URL mapping
├── recommendations/          # OTC drug guide, specialists, and hospital services
│   ├── models.py             # Specialist, Disease description, OTC Medicine, RecommendationHistory tables
│   ├── views.py              # GetRecommendationByDiseaseView and MedicinesMapsView
│   └── urls.py               # Recommendations & hospitals URLs
├── templates/                # Custom HTML templates
│   ├── base.html             # Base framework layout (navbar, footer, theme colors)
│   ├── accounts/             # Login, signup, and profile templates
│   ├── dashboard/            # Landing page (landing.html), Health Home (index.html), reports.html, chatbot.html
│   └── recommendations/      # Medicines and Maps dashboard (medicines_maps.html)
├── static/
│   └── css/
│       └── styles.css        # Clinical theme styles (gradients, animations, SVGs)
├── db.sqlite3                # Local development database
├── manage.py                 # Django CLI tool
├── requirements.txt          # Python dependencies (scikit-learn, django, pandas, etc.)
└── .env.example              # Sample environment file
```

---

## 🛠️ Step-by-Step Installation & Setup

### 1. Set Up Virtual Environment
Open your terminal in the project directory and execute:
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Setup Environment Variables
Create a file named `.env` in the root folder and configure:
```ini
DEBUG=True
SECRET_KEY=django-insecure-medwise-project-secret-key-change-this
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 4. Apply Database Migrations & Create Admin User
```powershell
# Apply database schemas (CustomUser, HealthProfile, DailyWellness, Predictions)
python manage.py migrate

# Create an administrator
python manage.py createsuperuser
```

### 5. Launch the Development Server
```powershell
python manage.py runserver
```
*   **Web Portal**: Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser. (The splash screen will load for 2.5 seconds on first access before opening the landing page).
*   **Admin Console**: Open [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) to manage biometric records and telemetry profiles.

---

## 🔌 Core API Endpoints

All prediction and recommendations endpoints require authenticated request sessions.

| Method | Endpoint | Description | Payload Example |
| :--- | :--- | :--- | :--- |
| **POST** | `/api/predict` | Infers disease from symptom list | `{"symptoms": ["itching", "skin_rash"]}` |
| **POST** | `/api/recommendations` | Fetches precautions, diet, specialist, and OTC meds | `{"prediction_id": "uuid-here"}` |
| **POST** | `/api/hospitals` | Finds nearby hospitals based on coordinates | `{"latitude": 23.25, "longitude": 77.41}` |
| **POST** | `/dashboard/wellness/update/` | Logs daily variables (water, sleep, steps, heart rate) | `{"water": 1800, "sleep": 7.5}` |
| **GET** | `/api/history` | Fetches user's prediction history logs | *None* |
| **GET** | `/api/symptoms` | Lists all 132 symptoms recognized by the model | *None* |

---

## 🧪 Running Automated Tests
Run unit tests to verify authentication paths, database models, redirect logs, and API view responses:
```powershell
python manage.py test
```
