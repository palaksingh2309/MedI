# 🩺 MedIntel AI — Clinical Diagnostics & Health Companion Platform

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.0%2B-092E20.svg?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.4.0-F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Build-Passing-emerald.svg?style=for-the-badge)](#)

**MedIntel AI** is a state-of-the-art clinical health companion and AI diagnostics web application. Built with **Django** and **Scikit-Learn Machine Learning**, MedIntel empowers patients and healthcare practitioners with high-precision disease prediction, dynamic health telemetry, AI-assisted medical report summarization, real-time medical chatbot support, and localized healthcare recommendations.

---

## 📋 Table of Contents

- [✨ Key Features](#-key-features)
- [🏗️ System Architecture](#️-system-architecture)
- [💻 Tech Stack](#-tech-stack)
- [📁 Project Structure](#-project-structure)
- [⚙️ Installation & Quick Start](#️-installation--quick-start)
- [🔌 REST API Reference](#-rest-api-reference)
- [🧪 Testing & Quality Assurance](#-testing--quality-assurance)
- [⚠️ Medical Disclaimer](#️-medical-disclaimer)

---

## ✨ Key Features

### 👥 1. Patient Biometrics & Dynamic BMI Companion
* **Custom Django User Model**: Extended authentication supporting patient profile photos, DOB, and emergency contacts.
* **Dynamic BMI Diagnostics Engine**: Computes BMI instantly from weight ($kg$) and height ($cm$), generating instant clinical categories (e.g. *Healthy Weight*, *Overweight*, *Obesity*) and custom actionable guidance.
* **Personalized Health Targets**: Track custom hydration targets, sleep goals, and daily physical activity targets.

### 🧠 2. ML-Powered Disease Inference Engine
* **Random Forest Classifier**: Trained on 132 distinct symptoms optimized via `GridSearchCV` hyperparameter tuning.
* **Top-3 Alternate Diagnoses**: Calculates probability distributions to display primary diagnosis alongside visual confidence meters and secondary diagnostic possibilities.
* **Precautions & Specialist Referral**: Automatically maps inferred conditions to OTC medications, lifestyle precautions, and specialized medical departments.
* **Rate Limiting & Logging**: Protected by sliding-window rate limiters (20 predictions/min) and diagnostic latency metrics database logging.

### 🏠 3. Interactive Health Home & Telemetry Dashboard
* **Dynamic Health Score Index**: A 100-point composite score dynamically updated based on active daily biometrics (BMI, hydration, sleep, steps).
* **Interactive Metric Dials**: Circular progress meters for logging daily water, sleep, steps, and exercise.
* **Telemetry Analytics**: Responsive line graphs powered by Chart.js tracking biometric changes over weekly intervals.
* **Real-Time Predictions Feed**: Background AJAX stream polling recent diagnoses without requiring page refreshes.
* **Emergency SOS Module**: Instant access to emergency hotlines, first-aid protocols (stroke, choking, severe burns), and nearest hospital dispatch.

### 💬 4. AI Medical Chatbot
* Responsive clinical messaging interface with typing indicators, distinct user/bot speech bubbles, clinical safety warnings, and one-tap triage prompt chips.

### 📄 5. Medical Report Summarizer
* Drag-and-drop file uploader supporting PDF and image reports.
* Simulated hematology and lab variable parser with skeleton shimmer progress bars and structured biomarker findings.

### 💊 6. OTC Medicines & Local Hospital Locator
* Interactive OTC medicine reference guide searchable by symptoms and disease name.
* Geolocation-enabled hospital finder providing nearby facility locations, distance indicators, and direct contact numbers.

---

## 🏗️ System Architecture

```text
               ┌──────────────────────────────────────────┐
               │              Client Browser              │
               │  (HTML5 / Modern Glassmorphic CSS / JS)  │
               └────────────────────┬─────────────────────┘
                                    │
                                    ▼
               ┌──────────────────────────────────────────┐
               │          Django Web Framework            │
               │   (URLs, Views, Forms, Middleware)       │
               └──────┬────────────────────────────┬──────┘
                      │                            │
                      ▼                            ▼
  ┌───────────────────────┐            ┌───────────────────────┐
  │   SQLite Database     │            │  ML Inference Engine  │
  │ (User, HealthProfile, │            │ (Random Forest Model, │
  │  Predictions, Logs)   │            │  Encoder, CSV Lookup) │
  └───────────────────────┘            └───────────────────────┘
```

---

## 💻 Tech Stack

* **Backend**: Django 5.0+, Python 3.10+
* **Machine Learning**: Scikit-Learn 1.4+, Pandas, NumPy, Joblib
* **Frontend**: HTML5, Vanilla CSS3 (Custom Design System, Glassmorphism, Micro-animations), JavaScript ES6+
* **Data Visualization**: Chart.js, FontAwesome 6
* **Database**: SQLite3 (Development / Production ready with PostgreSQL)

---

## 📁 Project Structure

```text
MedIntel/
├── medintel/                 # Core Django project configuration
│   ├── settings.py           # Database, middleware, static files config
│   ├── urls.py               # Root URL router
│   └── wsgi.py               # WSGI web server entry point
├── accounts/                 # User authentication & health profiles
│   ├── models.py             # CustomUser model (profile picture, dob, etc.)
│   ├── views.py              # Auth controllers (signup, login, profile view)
│   └── forms.py              # Profile & biometric form handlers
├── dashboard/                # Main patient health workspace
│   ├── models.py             # HealthProfile & DailyWellness models
│   ├── views.py              # Dashboard, Chatbot, Report Summarizer controllers
│   └── urls.py               # Dashboard routes
├── prediction/               # ML Disease Predictor subsystem
│   ├── datasets/             # Symptom & disease CSV reference files
│   ├── models/               # Serialized ML models (.pkl files)
│   ├── services/
│   │   └── predictor.py      # Disease inference engine
│   ├── views.py              # Predict REST API views
│   └── utils.py              # Rate limiting & clinical logging helpers
├── recommendations/          # OTC drug guide & hospital locator
│   ├── models.py             # Specialist, OTC Medicine, Disease info models
│   └── views.py              # Recommendations & Hospital API controllers
├── templates/                # Responsive HTML5 Django templates
│   ├── base.html             # Master layout template
│   ├── accounts/             # Login, signup, and profile views
│   ├── dashboard/            # Health Home, Chatbot, Report view templates
│   ├── prediction/           # Interactive symptom predictor view
│   └── recommendations/      # Medicines and maps view
├── static/
│   └── css/
│       └── styles.css        # Clinical CSS design system & micro-animations
├── manage.py                 # Django management CLI tool
├── requirements.txt          # Python dependencies manifest
└── README.md                 # Project documentation
```

---

## ⚙️ Installation & Quick Start

### 1. Prerequisites
Ensure you have **Python 3.10+** installed on your system.

### 2. Clone Repository & Setup Virtual Environment
```bash
# Clone the repository
git clone https://github.com/palaksingh2309/MedIntel.git
cd MedIntel

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```ini
DEBUG=True
SECRET_KEY=django-insecure-medintel-clinical-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Run Database Migrations & Create Superuser
```bash
# Apply database schemas
python manage.py migrate

# Create administrator account
python manage.py createsuperuser
```

### 6. Launch Development Server
```bash
python manage.py runserver
```
Navigate to **`http://127.0.0.1:8000/`** in your browser. Access the admin panel at **`http://127.0.0.1:8000/admin/`**.

---

## 🔌 REST API Reference

All REST endpoints accept standard `application/json` content types and require an active user session.

| Method | Endpoint | Description | Sample Request Payload |
| :--- | :--- | :--- | :--- |
| **POST** | `/api/predict` | Predict disease from list of symptoms | `{"symptoms": ["itching", "skin_rash", "nodal_skin_eruptions"]}` |
| **POST** | `/api/recommendations` | Get precautions, specialists & OTC meds | `{"prediction_id": "8f1a2b3c-4d5e-6f7a-8b9c-0d1e2f3a4b5c"}` |
| **POST** | `/api/hospitals` | Search nearby hospitals by coordinates | `{"latitude": 23.2599, "longitude": 77.4126}` |
| **POST** | `/dashboard/wellness/update/` | Log daily health telemetry variables | `{"water": 2000, "sleep": 7.5, "steps": 8500}` |
| **GET** | `/api/history` | Retrieve past diagnostic inference history | *None* |
| **GET** | `/api/symptoms` | Fetch complete list of supported symptoms | *None* |

---

## 🧪 Testing & Quality Assurance

Run the built-in Django automated unit test suite to verify authentication, health biometrics, ML predictor logic, and API view endpoints:

```bash
python manage.py test
```

All test cases must report `OK`.

---

## ⚠️ Medical Disclaimer

> **IMPORTANT**: MedIntel AI is an educational and clinical diagnostic support tool powered by machine learning algorithms. It is **NOT** a replacement for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider for medical concerns. In case of a medical emergency, immediately contact your local emergency services hotline.

---

<p center="align">
  Crafted with ❤️ for healthcare innovation.
</p>
