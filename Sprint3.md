# Sprint 3 (Week 3)

# Intelligent Medicine Recommendation & Nearby Hospital Finder

## Sprint Goal

Transform the disease prediction into a practical health assistant. After predicting a disease, the system should:

* Suggest safe first-aid guidance and general precautions.
* Recommend only **general/over-the-counter (OTC)** medicines where appropriate, with clear disclaimers.
* Recommend the appropriate medical specialist.
* Suggest nearby hospitals based on the user's location.
* Store all recommendations in the user's history.
* Display everything in a clean dashboard.

> **Important:** This project should **never prescribe prescription medicines or dosages**. It should clearly state that recommendations are informational and not a substitute for professional medical advice.

---

# Production Architecture

```text
User

↓

Disease Prediction (Sprint 2)

↓

Recommendation Engine

├── Precautions
├── Home Remedies
├── Diet Suggestions
├── OTC Medicines (where appropriate)
├── Specialist Recommendation
└── Nearby Hospitals

↓

Supabase

↓

Dashboard
```

---

# Folder Structure

```text
hospitals/

│
├── services/
│     hospital_service.py
│
├── utils/
│     location.py
│
├── views.py
├── urls.py
└── models.py


recommendations/

│
├── services/
│      recommendation_engine.py
│
├── data/
│      disease_info.json
│      medicines.json
│      specialists.json
│
├── views.py
└── urls.py
```

---

# Phase 1 — Disease Knowledge Base

Instead of hardcoding information, create a structured knowledge base.

Example:

```json
{
  "Typhoid": {
    "description": "...",
    "precautions": [],
    "diet": [],
    "home_remedies": [],
    "specialist": "General Physician"
  }
}
```

Eventually this should live in Supabase.

---

# Supabase Tables

## diseases

| Column       | Type |
| ------------ | ---- |
| id           | UUID |
| disease_name | Text |
| description  | Text |
| causes       | Text |
| symptoms     | JSON |
| precautions  | JSON |
| diet         | JSON |
| specialist   | Text |

---

## medicines

| Column        | Type    |
| ------------- | ------- |
| id            | UUID    |
| disease_id    | UUID    |
| medicine_name | Text    |
| medicine_type | Text    |
| otc           | Boolean |
| description   | Text    |
| precautions   | Text    |

---

## specialists

| Column      | Type |
| ----------- | ---- |
| id          | UUID |
| specialist  | Text |
| description | Text |

---

## hospitals

(optional cache)

| Column        | Type  |
| ------------- | ----- |
| id            | UUID  |
| hospital_name | Text  |
| latitude      | Float |
| longitude     | Float |
| phone         | Text  |

---

# Phase 2 — Recommendation Engine

Create

```text
recommendation_engine.py
```

Responsibilities

```
Input Disease

↓

Fetch Disease Details

↓

Fetch Medicines

↓

Fetch Diet

↓

Fetch Home Remedies

↓

Fetch Specialist

↓

Return JSON
```

The Django view should never contain business logic.

---

# Response Example

```json
{
  "disease":"Typhoid",

  "description":"...",

  "precautions":[
      "...",
      "..."
  ],

  "diet":[
      "...",
      "..."
  ],

  "home_remedies":[
      "...",
      "..."
  ],

  "specialist":"General Physician",

  "medicines":[]
}
```

---

# Medicine Recommendation

Instead of simply displaying medicine names,

show

```text
Medicine

Purpose

OTC or Prescription

Warnings

Side Effects

Consult Doctor?
```

Example

```
Paracetamol

Purpose:
Temporary fever reduction

Type:
OTC

Warning:
Avoid exceeding the recommended label dosage.

Doctor Consultation:
Yes, if symptoms persist or worsen.
```

This is much safer.

---

# Production Validation

Suppose disease is

```
Common Cold
```

Only OTC medicines appear.

If disease is

```
Pneumonia
```

No medicines appear.

Instead

```
Prescription treatment required.

Please consult a physician immediately.
```

This prevents unsafe recommendations.

---

# Phase 3 — Diet Recommendation

Example

```
Typhoid

Recommended

✔ Boiled vegetables

✔ Rice

✔ Bananas

✔ Plenty of fluids

Avoid

✖ Oily food

✖ Spicy food

✖ Alcohol
```

Store these inside Supabase.

---

# Phase 4 — Home Remedies

Example

```
Common Cold

Warm fluids

Steam inhalation

Adequate hydration

Rest
```

Never display dangerous advice.

---

# Phase 5 — Specialist Recommendation

Instead of only disease,

recommend

```
Disease

↓

Specialist
```

Example

```
Migraine

↓

Neurologist
```

```
Asthma

↓

Pulmonologist
```

```
Diabetes

↓

Endocrinologist
```

---

# Phase 6 — Nearby Hospitals

Use the user's location.

Possible APIs

### Option 1 (Recommended)

Google Places API

Pros

* Excellent accuracy
* Ratings
* Photos
* Open/Closed status

Cons

* Paid beyond free quota

---

### Option 2

OpenStreetMap + Overpass API

Pros

* Free
* No billing

Cons

* Less detailed

---

# User Flow

```
Predict Disease

↓

Allow Location Access

↓

Get Latitude

↓

Hospital API

↓

Nearest Hospitals

↓

Display Map
```

---

# Hospital Information

Display

```
Hospital Name

Distance

Address

Phone Number

Open Status

Rating

Navigation Button
```

---

# Interactive Map

Instead of a simple list,

show

```
Current Location

↓

Interactive Map

↓

Hospital Markers
```

Clicking a marker opens

```
Hospital

Distance

Phone

Directions
```

---

# Emergency Priority

If predicted disease belongs to

```
Emergency Category
```

Example

```
Stroke

Heart Attack

Severe Asthma Attack
```

Instead of medicine

display

```
Seek emergency medical care immediately.

Call your local emergency services or go to the nearest emergency department.
```

---

# Recommendation History

Create

```
recommendation_history
```

Supabase Table

| Column        | Type      |
| ------------- | --------- |
| id            | UUID      |
| user_id       | UUID      |
| prediction_id | UUID      |
| disease       | Text      |
| specialist    | Text      |
| viewed_at     | Timestamp |

---

# API Design

## Recommendation API

```
POST

/api/recommendations
```

Input

```json
{
  "prediction_id":"..."
}
```

Output

```json
{
  "disease":"Typhoid",

  "specialist":"General Physician",

  "precautions":[],

  "diet":[],

  "medicines":[],

  "home_remedies":[]
}
```

---

## Nearby Hospitals API

```
POST

/api/hospitals
```

Input

```json
{
    "latitude":23.25,
    "longitude":77.41
}
```

Response

```json
[
   {
      "name":"City Hospital",
      "distance":"2.3 km",
      "rating":4.5
   }
]
```

---

# Frontend Flow

```
Dashboard

↓

Choose Symptoms

↓

Predict Disease

↓

Disease Card

↓

Confidence Score

↓

Recommendation Tabs

│

├── Overview

├── Precautions

├── Diet

├── Home Remedies

├── Medicines

├── Specialist

└── Nearby Hospitals
```

---

# Production-Ready Features

### Loading States

```
Finding Hospitals...

Generating Recommendations...
```

---

### Error Handling

If location permission is denied:

```
Location permission denied.

Please enable location services or search by city.
```

If the hospital API fails:

```
Unable to fetch nearby hospitals.

Please try again later.
```

---

### Caching

Hospital data changes infrequently. Cache nearby hospital results (based on rounded coordinates) for a short period to reduce API calls and improve performance.

---

### Security

* Validate latitude and longitude ranges.
* Rate-limit hospital lookup APIs.
* Never expose API keys in the frontend.
* Sanitize all responses before displaying them.
* Use HTTPS in production.

---

# Deliverables

By the end of Sprint 3, your application should support:

* ✅ Disease information dashboard
* ✅ Precautions and lifestyle recommendations
* ✅ Diet suggestions
* ✅ Home remedies
* ✅ Safe OTC medicine information with disclaimers
* ✅ Appropriate specialist recommendation
* ✅ Nearby hospital search with interactive map
* ✅ Recommendation history stored in Supabase
* ✅ Production-ready REST APIs with validation and error handling
* ✅ Responsive UI with loading, empty, and error states

At the end of Sprint 3, your AI Health Assistant will evolve from a **disease prediction model** into a **decision-support system** that provides useful next steps while avoiding unsafe medical advice. This is a much stronger demonstration of real-world software engineering and responsible AI design.
