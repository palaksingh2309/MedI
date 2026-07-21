import os
import urllib.request
import pandas as pd
import numpy as np

# URLs to the raw datasets on GitHub
URL_TRAINING = "https://raw.githubusercontent.com/yash-naikk/HEALTH-CARE-CHATBOT/master/Training.csv"
URL_TESTING = "https://raw.githubusercontent.com/yash-naikk/HEALTH-CARE-CHATBOT/master/Testing.csv"
URL_DESCRIPTION = "https://raw.githubusercontent.com/yash-naikk/HEALTH-CARE-CHATBOT/master/symptom_Description.csv"
URL_PRECAUTION = "https://raw.githubusercontent.com/yash-naikk/HEALTH-CARE-CHATBOT/master/symptom_precaution.csv"

# Target local paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASETS_DIR = os.path.join(BASE_DIR, "datasets")

PATH_SYMPTOMS = os.path.join(DATASETS_DIR, "symptoms.csv")
PATH_DESCRIPTION = os.path.join(DATASETS_DIR, "symptom_description.csv")
PATH_PRECAUTION = os.path.join(DATASETS_DIR, "symptom_precaution.csv")

def download_file(url, dest):
    print(f"Downloading {url} to {dest}...")
    urllib.request.urlretrieve(url, dest)

def clean_symptoms():
    """
    Downloads and merges Training.csv and Testing.csv,
    cleans duplicate rows, nulls, and normalizes column names.
    """
    os.makedirs(DATASETS_DIR, exist_ok=True)
    
    temp_train = os.path.join(DATASETS_DIR, "temp_train.csv")
    temp_test = os.path.join(DATASETS_DIR, "temp_test.csv")
    
    download_file(URL_TRAINING, temp_train)
    download_file(URL_TESTING, temp_test)
    
    df_train = pd.read_csv(temp_train)
    df_test = pd.read_csv(temp_test)
    
    # Merge datasets to create a single complete symptoms dataset
    df_merged = pd.concat([df_train, df_test], ignore_index=True)
    
    # Remove temporary files
    if os.path.exists(temp_train): os.remove(temp_train)
    if os.path.exists(temp_test): os.remove(temp_test)
    
    # Check for empty/extra columns (sometimes pandas imports empty trailing columns)
    df_merged = df_merged.loc[:, ~df_merged.columns.str.startswith('Unnamed:')]
    
    # Clean duplicate rows
    initial_shape = df_merged.shape
    df_merged = df_merged.drop_duplicates()
    print(f"Removed duplicates: Shape changed from {initial_shape} to {df_merged.shape}")
    
    # Drop rows with null target (prognosis) or all null symptoms
    df_merged = df_merged.dropna(subset=['prognosis'])
    
    # Normalize column names: strip spaces and lowercase them
    df_merged.columns = [col.strip().lower() for col in df_merged.columns]
    
    # Rename 'prognosis' to 'disease' to match Sprint 2 requirement
    df_merged = df_merged.rename(columns={'prognosis': 'disease'})
    
    # Strip whitespace from disease name rows
    df_merged['disease'] = df_merged['disease'].str.strip()
    
    # Save the cleaned dataset
    df_merged.to_csv(PATH_SYMPTOMS, index=False)
    print(f"Cleaned symptoms dataset saved to {PATH_SYMPTOMS}")
    return df_merged

def clean_description():
    """
    Downloads and normalizes the disease description CSV.
    """
    os.makedirs(DATASETS_DIR, exist_ok=True)
    
    download_file(URL_DESCRIPTION, PATH_DESCRIPTION)
    
    # Read description CSV (without headers in raw github file)
    df_desc = pd.read_csv(PATH_DESCRIPTION, header=None, names=['disease', 'description'])
    
    # Normalize values
    df_desc['disease'] = df_desc['disease'].astype(str).str.strip()
    df_desc['description'] = df_desc['description'].astype(str).str.strip()
    
    # Drop duplicate disease descriptions if any
    df_desc = df_desc.drop_duplicates(subset=['disease'])
    df_desc = df_desc.dropna()
    
    df_desc.to_csv(PATH_DESCRIPTION, index=False)
    print(f"Cleaned descriptions saved to {PATH_DESCRIPTION}")
    return df_desc

def clean_precaution():
    """
    Downloads and normalizes the precautions CSV.
    """
    os.makedirs(DATASETS_DIR, exist_ok=True)
    
    download_file(URL_PRECAUTION, PATH_PRECAUTION)
    
    # Read precaution CSV
    df_prec = pd.read_csv(PATH_PRECAUTION, header=None)
    
    # Re-structure columns: First is disease, rest are precautions
    cols = ['disease'] + [f'precaution_{i}' for i in range(1, len(df_prec.columns))]
    df_prec.columns = cols
    
    # Strip spaces
    df_prec['disease'] = df_prec['disease'].astype(str).str.strip()
    for col in cols[1:]:
        df_prec[col] = df_prec[col].astype(str).str.strip()
        # Replace empty strings / 'nan' with standard empty string
        df_prec[col] = df_prec[col].replace('nan', '')
    
    df_prec = df_prec.drop_duplicates(subset=['disease'])
    df_prec = df_prec.dropna()
    
    df_prec.to_csv(PATH_PRECAUTION, index=False)
    print(f"Cleaned precautions saved to {PATH_PRECAUTION}")
    return df_prec

def main():
    print("Starting preprocessing pipeline...")
    clean_symptoms()
    clean_description()
    clean_precaution()
    print("Preprocessing completed successfully!")

if __name__ == "__main__":
    main()
