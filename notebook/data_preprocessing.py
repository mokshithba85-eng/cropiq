import os
import pandas as pd
import numpy as np

def run_preprocessing():
    raw_path = os.path.join("dataset", "karnataka_agriculture_data.csv")
    cleaned_path = os.path.join("dataset", "karnataka_agriculture_cleaned.csv")
    
    if not os.path.exists(raw_path):
        print(f"Error: Raw dataset not found at {raw_path}")
        return False
        
    print(f"Loading raw dataset from {raw_path}...")
    df = pd.read_csv(raw_path)
    print(f"Raw dataset shape: {df.shape}")
    
    # 1. Rename columns to standardized names
    column_mapping = {
        'Location': 'District',
        'Soil type': 'Soil_Type',
        'Rainfall': 'Rainfall_mm',
        'Temperature': 'Temperature_C',
        'yeilds': 'Yield_Kg_Ha',
        'Crops': 'Crop',
        'price': 'Price',
        'Area': 'Area_Hectares',
        'Season': 'Season',
        'Humidity': 'Humidity_Percent',
        'Irrigation': 'Irrigation_Method',
        'Year': 'Year'
    }
    df.rename(columns=column_mapping, inplace=True)
    
    # 2. Handling Missing Values
    print("Checking for missing values:")
    print(df.isnull().sum())
    
    # Imputing temperature and rainfall with district/seasonal medians to maintain regional accuracy
    df['Temperature_C'] = df.groupby(['District', 'Season'])['Temperature_C'].transform(lambda x: x.fillna(x.median()))
    df['Rainfall_mm'] = df.groupby(['District', 'Season'])['Rainfall_mm'].transform(lambda x: x.fillna(x.median()))
    df['Humidity_Percent'] = df.groupby(['District', 'Season'])['Humidity_Percent'].transform(lambda x: x.fillna(x.median()))
    
    # Drop records where critical target fields (Crop, Yield) are missing
    df.dropna(subset=['Crop', 'Yield_Kg_Ha'], inplace=True)
    
    # 3. Standardizing Categorical Fields
    df['Season'] = df['Season'].str.strip().str.title()
    df['Soil_Type'] = df['Soil_Type'].str.strip().str.title()
    df['Crop'] = df['Crop'].str.strip().str.title()
    df['District'] = df['District'].str.strip().str.title()
    
    # 4. Outlier Handling (Cap yield anomalies exceeding 3 standard deviations from crop mean)
    print("Handling outliers...")
    for crop in df['Crop'].unique():
        crop_mask = df['Crop'] == crop
        crop_yields = df.loc[crop_mask, 'Yield_Kg_Ha']
        if len(crop_yields) > 0:
            mean_y = crop_yields.mean()
            std_y = crop_yields.std()
            upper_limit = mean_y + 3 * std_y
            # Cap values exceeding the 3-sigma limit to the limit
            df.loc[crop_mask & (df['Yield_Kg_Ha'] > upper_limit), 'Yield_Kg_Ha'] = upper_limit
            
    print(f"Cleaned dataset shape: {df.shape}")
    
    # 5. Export Cleaned Dataset
    print(f"Exporting cleaned dataset to {cleaned_path}...")
    df.to_csv(cleaned_path, index=False)
    print("Preprocessing completed successfully!")
    return True

if __name__ == "__main__":
    # Ensure working directory is the repo root if run from notebook/ folder
    if os.path.basename(os.getcwd()) == "notebook":
        os.chdir("..")
    run_preprocessing()
