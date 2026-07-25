import os
import csv
import json

# Define directories
BASE_DIR = 'p:/MedIntel'
RECOMMENDATIONS_DIR = os.path.join(BASE_DIR, 'recommendations')
DATA_DIR = os.path.join(RECOMMENDATIONS_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# List of all 41 diseases from model classes
classes = [
    '(vertigo) Paroymsal  Positional Vertigo', 'AIDS', 'Acne', 'Alcoholic hepatitis', 'Allergy', 'Arthritis', 
    'Bronchial Asthma', 'Cervical spondylosis', 'Chicken pox', 'Chronic cholestasis', 'Common Cold', 'Dengue', 
    'Diabetes ', 'Dimorphic hemmorhoids(piles)', 'Drug Reaction', 'Fungal infection', 'GERD', 'Gastroenteritis', 
    'Heart attack', 'Hepatitis B', 'Hepatitis C', 'Hepatitis D', 'Hepatitis E', 'Hypertension ', 'Hyperthyroidism', 
    'Hypoglycemia', 'Hypothyroidism', 'Impetigo', 'Jaundice', 'Malaria', 'Migraine', 'Osteoarthristis', 
    'Paralysis (brain hemorrhage)', 'Peptic ulcer diseae', 'Pneumonia', 'Psoriasis', 'Tuberculosis', 'Typhoid', 
    'Urinary tract infection', 'Varicose veins', 'hepatitis A'
]

# Specialist mapping
specialists_map = {
    'Fungal infection': 'Dermatologist',
    'Allergy': 'Allergist / Immunologist',
    'GERD': 'Gastroenterologist',
    'Chronic cholestasis': 'Gastroenterologist / Hepatologist',
    'Drug Reaction': 'Allergist / General Physician',
    'Peptic ulcer diseae': 'Gastroenterologist',
    'AIDS': 'Infectious Disease Specialist',
    'Diabetes ': 'Endocrinologist',
    'Gastroenteritis': 'Gastroenterologist',
    'Bronchial Asthma': 'Pulmonologist',
    'Hypertension ': 'Cardiologist / General Physician',
    'Migraine': 'Neurologist',
    'Cervical spondylosis': 'Orthopedist / Neurologist',
    'Paralysis (brain hemorrhage)': 'Neurologist / Neurosurgeon',
    'Jaundice': 'Gastroenterologist / Hepatologist',
    'Malaria': 'Infectious Disease Specialist',
    'Chicken pox': 'General Physician / Pediatrician',
    'Dengue': 'Infectious Disease Specialist / General Physician',
    'Typhoid': 'Infectious Disease Specialist / General Physician',
    'hepatitis A': 'Gastroenterologist / Hepatologist',
    'Hepatitis B': 'Gastroenterologist / Hepatologist',
    'Hepatitis C': 'Gastroenterologist / Hepatologist',
    'Hepatitis D': 'Gastroenterologist / Hepatologist',
    'Hepatitis E': 'Gastroenterologist / Hepatologist',
    'Alcoholic hepatitis': 'Gastroenterologist / Hepatologist',
    'Tuberculosis': 'Pulmonologist / Infectious Disease Specialist',
    'Common Cold': 'General Physician',
    'Pneumonia': 'Pulmonologist',
    'Dimorphic hemmorhoids(piles)': 'General Surgeon / Gastroenterologist',
    'Heart attack': 'Cardiologist',
    'Varicose veins': 'Vascular Surgeon / Dermatologist',
    'Hypothyroidism': 'Endocrinologist',
    'Hyperthyroidism': 'Endocrinologist',
    'Hypoglycemia': 'Endocrinologist / General Physician',
    'Osteoarthristis': 'Rheumatologist / Orthopedist',
    'Arthritis': 'Rheumatologist / Orthopedist',
    '(vertigo) Paroymsal  Positional Vertigo': 'ENT Specialist / Neurologist',
    'Urinary tract infection': 'Urologist / General Physician',
    'Acne': 'Dermatologist',
    'Impetigo': 'Dermatologist',
    'Psoriasis': 'Dermatologist'
}

# Diet mapping
diet_map = {
    'GERD': {
        'recommended': ['Oatmeal', 'Bananas', 'Ginger tea', 'Leafy greens', 'Lean poultry'],
        'avoid': ['Citrus fruits', 'Tomato-based foods', 'Chocolate', 'Caffeine', 'Fried foods', 'Spicy foods']
    },
    'Diabetes ': {
        'recommended': ['Whole grains', 'Leafy greens', 'Beans', 'Berries', 'Fish (rich in Omega-3)'],
        'avoid': ['Sugary drinks', 'Trans fats', 'White bread', 'Sweetened cereals', 'Fruit juice']
    },
    'Hypertension ': {
        'recommended': ['Garlic', 'Berries', 'Leafy greens', 'Oatmeal', 'Bananas', 'Low-fat dairy'],
        'avoid': ['Table salt', 'Processed meat', 'Canned soups', 'Frozen pizza', 'Alcohol']
    },
    'Common Cold': {
        'recommended': ['Warm chicken soup', 'Herbal tea', 'Citrus fruits', 'Honey', 'Garlic', 'Ginger'],
        'avoid': ['Ice cream', 'Cold drinks', 'Alcohol', 'Sugary foods']
    },
    'Typhoid': {
        'recommended': ['Boiled vegetables', 'Rice', 'Bananas', 'Plenty of fluids', 'Broth'],
        'avoid': ['Oily food', 'Spicy food', 'Alcohol', 'Raw fruits and vegetables']
    },
    'Malaria': {
        'recommended': ['Fresh fruits', 'Boiled rice', 'Steamed vegetables', 'Coconut water', 'Light soups'],
        'avoid': ['Oily food', 'Spicy food', 'Heavy non-veg meals', 'Junk food']
    },
    'Gastroenteritis': {
        'recommended': ['Bananas', 'Rice', 'Applesauce', 'Toast (BRAT diet)', 'ORS', 'Clear broths'],
        'avoid': ['Dairy products', 'Caffeine', 'Nicotine', 'Fatty foods', 'Highly seasoned foods']
    },
    'Peptic ulcer diseae': {
        'recommended': ['Probiotic foods (yogurt)', 'Apples', 'Oatmeal', 'Broccoli', 'Olive oil'],
        'avoid': ['Spicy foods', 'Acidic foods', 'Caffeine', 'Alcohol', 'Processed meats']
    },
    'Fungal infection': {
        'recommended': ['Garlic', 'Yogurt', 'Coconut oil', 'Leafy green vegetables', 'Ginger'],
        'avoid': ['Sugar', 'Yeast-containing foods', 'Alcohol', 'Refined carbs']
    },
    'Acne': {
        'recommended': ['Foods rich in Zinc (pumpkin seeds)', 'Omega-3 fatty acids', 'Leafy greens', 'Hydrating fruits'],
        'avoid': ['High-glycemic foods', 'Dairy products', 'Excessive chocolate', 'Fast food']
    },
    'Psoriasis': {
        'recommended': ['Anti-inflammatory foods (salmon, olive oil)', 'Berries', 'Spinach', 'Turmeric'],
        'avoid': ['Red meat', 'Dairy', 'Gluten', 'Processed foods', 'Alcohol']
    }
}

# Home Remedies mapping
remedies_map = {
    'Common Cold': ['Steam inhalation', 'Gargle with warm salt water', 'Stay hydrated', 'Get plenty of rest'],
    'Typhoid': ['Bed rest', 'Warm sponge baths for high fever', 'Electrolyte replacement fluids (ORS)', 'Adequate hydration'],
    'Malaria': ['Cold compress for fever', 'Drink plenty of water and juices', 'Complete bed rest'],
    'Gastroenteritis': ['Stay hydrated with small sips of water', 'Rest the stomach', 'Avoid solid food for a few hours', 'Take electrolyte solutions'],
    'GERD': ['Drink water', 'Avoid lying down after meals', 'Elevate the head of the bed', 'Wear loose clothing'],
    'Diabetes ': ['Regular physical activity', 'Monitor blood sugar levels', 'Stay hydrated', 'Manage stress levels'],
    'Hypertension ': ['Daily cardiovascular exercise', 'Practice deep breathing or meditation', 'Limit caffeine intake', 'Reduce sodium in diet'],
    'Acne': ['Wash face gently twice a day', 'Avoid popping or picking pimples', 'Apply tea tree oil dilute', 'Keep hair clean and off the face'],
    'Fungal infection': ['Keep the area dry and clean', 'Wear loose-fitting cotton clothing', 'Apply diluted tea tree oil', 'Do not scratch the area'],
    'Migraine': ['Rest in a quiet, dark room', 'Apply a cold compress to the forehead', 'Practice relaxation techniques', 'Stay hydrated'],
    '(vertigo) Paroymsal  Positional Vertigo': ['Perform Epley maneuver', 'Lie down in a comfortable position', 'Avoid sudden head movements', 'Rise slowly from bed'],
    'Urinary tract infection': ['Drink plenty of water', 'Drink unsweetened cranberry juice', 'Urinate frequently', 'Apply a heating pad for comfort']
}

# Medicine mapping (OTC only)
medicine_templates = {
    'Common Cold': [
        {
            'medicine_name': 'Paracetamol',
            'medicine_type': 'OTC',
            'otc': True,
            'description': 'Temporary fever reduction and relief of mild to moderate body aches.',
            'precautions': 'Avoid exceeding the recommended label dosage. Do not take with other paracetamol-containing products.'
        },
        {
            'medicine_name': 'Loratadine',
            'medicine_type': 'OTC',
            'otc': True,
            'description': 'Non-drowsy antihistamine for runny nose and sneezing.',
            'precautions': 'May cause dry mouth or mild drowsiness in rare cases.'
        }
    ],
    'GERD': [
        {
            'medicine_name': 'Calcium Carbonate (Antacid)',
            'medicine_type': 'OTC',
            'otc': True,
            'description': 'Fast-acting relief from heartburn and acid indigestion.',
            'precautions': 'Do not use for more than 2 weeks without consulting a doctor.'
        },
        {
            'medicine_name': 'Famotidine',
            'medicine_type': 'OTC',
            'otc': True,
            'description': 'H2 blocker that reduces acid production in the stomach.',
            'precautions': 'Take 15-60 minutes before eating food that causes heartburn.'
        }
    ],
    'Allergy': [
        {
            'medicine_name': 'Cetirizine',
            'medicine_type': 'OTC',
            'otc': True,
            'description': 'Antihistamine for relief of allergy symptoms like watery eyes, runny nose, and itching.',
            'precautions': 'Avoid alcohol. May cause drowsiness in some users.'
        }
    ],
    'Acne': [
        {
            'medicine_name': 'Benzoyl Peroxide 2.5% Gel',
            'medicine_type': 'OTC',
            'otc': True,
            'description': 'Topical treatment to kill acne-causing bacteria and help clear skin.',
            'precautions': 'Can cause skin dryness and peeling. Avoid contact with eyes and bleached fabrics.'
        }
    ],
    'Fungal infection': [
        {
            'medicine_name': 'Clotrimazole 1% Cream',
            'medicine_type': 'OTC',
            'otc': True,
            'description': 'Topical antifungal cream to treat athlete\'s foot, jock itch, and ringworm.',
            'precautions': 'Apply to affected area as directed. For external use only.'
        }
    ],
    'Dimorphic hemmorhoids(piles)': [
        {
            'medicine_name': 'Witch Hazel Pads',
            'medicine_type': 'OTC',
            'otc': True,
            'description': 'Soothing pads to relieve local itching and discomfort associated with hemorrhoids.',
            'precautions': 'Use after bowel movements or up to 6 times daily.'
        }
    ],
    'Osteoarthristis': [
        {
            'medicine_name': 'Acetaminophen',
            'medicine_type': 'OTC',
            'otc': True,
            'description': 'Pain reliever for mild osteoarthritis joint pain.',
            'precautions': 'Strictly adhere to dosage limits to avoid liver damage.'
        }
    ],
    'Arthritis': [
        {
            'medicine_name': 'Ibuprofen',
            'medicine_type': 'OTC',
            'otc': True,
            'description': 'Nonsteroidal anti-inflammatory drug (NSAID) to reduce joint pain and swelling.',
            'precautions': 'Take with food to prevent stomach upset. Avoid long-term unmonitored use.'
        }
    ],
    'Migraine': [
        {
            'medicine_name': 'Ibuprofen',
            'medicine_type': 'OTC',
            'otc': True,
            'description': 'Pain reliever to reduce migraine-associated headache pain.',
            'precautions': 'Take at the onset of migraine symptoms. Do not overuse.'
        }
    ],
    '(vertigo) Paroymsal  Positional Vertigo': [
        {
            'medicine_name': 'Meclizine',
            'medicine_type': 'OTC',
            'otc': True,
            'description': 'Antihistamine used to treat or prevent dizziness and motion sickness.',
            'precautions': 'May cause significant drowsiness. Avoid driving or operating machinery.'
        }
    ],
    'Urinary tract infection': [
        {
            'medicine_name': 'Phenazopyridine',
            'medicine_type': 'OTC',
            'otc': True,
            'description': 'Urinary tract analgesic to relieve burning, pain, and urgency.',
            'precautions': 'Informational: This does NOT cure the infection. You must consult a doctor for prescription antibiotics.'
        }
    ]
}

# 1. Load descriptions from CSV
descriptions = {}
desc_path = os.path.join(BASE_DIR, 'prediction', 'datasets', 'symptom_description.csv')
with open(desc_path, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        norm_name = row['disease'].strip()
        # Handle some spelling maps to align with model classes
        if norm_name == 'Hypertension':
            norm_name = 'Hypertension '
        elif norm_name == 'Diabetes':
            norm_name = 'Diabetes '
        elif norm_name == 'Dimorphic hemorrhoids(piles)':
            norm_name = 'Dimorphic hemmorhoids(piles)'
        
        descriptions[norm_name] = row['description'].strip()

# 2. Load precautions from CSV
precautions = {}
prec_path = os.path.join(BASE_DIR, 'prediction', 'datasets', 'symptom_precaution.csv')
with open(prec_path, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        norm_name = row['disease'].strip()
        if norm_name == 'Hypertension':
            norm_name = 'Hypertension '
        elif norm_name == 'Diabetes':
            norm_name = 'Diabetes '
        elif norm_name == 'Dimorphic hemmorhoids(piles)':
            norm_name = 'Dimorphic hemmorhoids(piles)'
            
        prec_list = []
        for i in range(1, 5):
            val = row.get(f'precaution_{i}', '').strip()
            if val:
                prec_list.append(val.capitalize())
        precautions[norm_name] = prec_list

# Generate disease_info.json
disease_info = {}
all_medicines = []

# Fallbacks
fallback_diet = {
    'recommended': ['Balanced diet', 'Fresh fruits', 'Steamed vegetables', 'Whole grains', 'Plenty of water'],
    'avoid': ['High-sodium foods', 'Processed foods', 'Excess sugar', 'Alcohol', 'Oily/spicy dishes']
}
fallback_remedies = ['Get adequate rest', 'Stay well-hydrated', 'Monitor symptoms closely', 'Consult a doctor if symptoms worsen']

for cls_name in classes:
    desc = descriptions.get(cls_name, 'No description available.')
    # If the CSV didn't match directly, try lowercase key search
    if desc == 'No description available.':
        for k, v in descriptions.items():
            if k.lower().strip() == cls_name.lower().strip():
                desc = v
                break
                
    precs = precautions.get(cls_name, [])
    if not precs:
        for k, v in precautions.items():
            if k.lower().strip() == cls_name.lower().strip():
                precs = v
                break
                
    spec = specialists_map.get(cls_name, 'General Physician')
    diet = diet_map.get(cls_name, fallback_diet)
    remedies = remedies_map.get(cls_name, fallback_remedies)
    
    # Structure for disease_info.json
    disease_info[cls_name] = {
        'description': desc,
        'precautions': precs,
        'diet': diet,
        'home_remedies': remedies,
        'specialist': spec
    }
    
    # Medicines for medicines.json
    meds = medicine_templates.get(cls_name, [])
    if meds:
        for med in meds:
            all_medicines.append({
                'disease_name': cls_name,
                'medicine_name': med['medicine_name'],
                'medicine_type': med['medicine_type'],
                'otc': med['otc'],
                'description': med['description'],
                'precautions': med['precautions']
            })

# Specialists definitions
unique_specs = sorted(list(set(specialists_map.values())))
specialists = []
for spec in unique_specs:
    desc = f"Specialist medical practitioner in the field of {spec.split(' / ')[0]}."
    if spec == 'General Physician':
        desc = "A primary care physician who provides preventive care and treats a wide variety of common medical conditions."
    elif spec == 'Dermatologist':
        desc = "A medical practitioner qualified to diagnose and treat skin disorders."
    elif spec == 'Cardiologist':
        desc = "A doctor who specializes in diagnosing and treating diseases of the cardiovascular system."
    elif spec == 'Neurologist':
        desc = "A medical specialist in the diagnosis and treatment of disorders of the nervous system."
    elif spec == 'Gastroenterologist':
        desc = "A medical practitioner who specializes in the diagnosis and treatment of disorders of the digestive system."
    elif spec == 'Pulmonologist':
        desc = "A medical doctor who diagnoses and treats conditions that affect the respiratory system."
    elif spec == 'Endocrinologist':
        desc = "A medical doctor who specializes in diagnosing and treating hormone-related conditions."
    elif spec == 'Infectious Disease Specialist':
        desc = "A doctor specializing in the diagnosis, control and treatment of infections."
    
    specialists.append({
        'specialist': spec,
        'description': desc
    })

# Write JSON files
with open(os.path.join(DATA_DIR, 'disease_info.json'), 'w', encoding='utf-8') as f:
    json.dump(disease_info, f, indent=2, ensure_ascii=False)
    
with open(os.path.join(DATA_DIR, 'medicines.json'), 'w', encoding='utf-8') as f:
    json.dump(all_medicines, f, indent=2, ensure_ascii=False)

with open(os.path.join(DATA_DIR, 'specialists.json'), 'w', encoding='utf-8') as f:
    json.dump(specialists, f, indent=2, ensure_ascii=False)

print(f"Generated {len(disease_info)} diseases, {len(all_medicines)} OTC medicines, and {len(specialists)} specialists in {DATA_DIR}.")
