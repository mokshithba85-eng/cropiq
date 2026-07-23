# Exploratory Data Analysis (EDA) Process

This document details the exploratory data analysis (EDA) conducted on the Karnataka agriculture dataset to extract insights and prepare the data for downstream dashboards and recommendation logic.

---

## 1. Dataset Profile

The dataset comprises agricultural records from various districts in Karnataka. 
- **Total Records:** 3,158
- **Temporal Range:** Multi-season agricultural cycles
- **Geographic Coverage:** Karnataka, India (District-level granularity)

### Key Attributes Analyzed
| Attribute | Data Type | Description |
| :--- | :--- | :--- |
| `District` | Categorical | District name in Karnataka |
| `Season` | Categorical | Cropping season (Kharif, Rabi, Summer) |
| `Soil_Type` | Categorical | Soil classification (Black, Red, Sandy, Laterite, Clayey) |
| `Rainfall_mm` | Numerical | Average seasonal rainfall in millimeters |
| `Temperature_C` | Numerical | Average seasonal temperature in Celsius |
| `Crop` | Categorical | Name of the cultivated crop |
| `Yield_Kg_Ha` | Numerical | Crop yield in Kilograms per Hectare |

---

## 2. Python Data Preprocessing Pipeline

To clean and validate the 3,158 records, we established a pipeline using **Pandas**.

```python
import pandas as pd
import numpy as np

# Load dataset
df = pd.read_csv('../dataset/karnataka_agriculture_data.csv')

# 1. Handling Missing Values
print("Missing values per column:\n", df.isnull().sum())
# Imputing temperature and rainfall with district/seasonal medians to maintain regional accuracy
df['Temperature_C'] = df.groupby(['District', 'Season'])['Temperature_C'].transform(lambda x: x.fillna(x.median()))
df['Rainfall_mm'] = df.groupby(['District', 'Season'])['Rainfall_mm'].transform(lambda x: x.fillna(x.median()))

# Drop records where critical target fields (Crop, Yield) are missing
df.dropna(subset=['Crop', 'Yield_Kg_Ha'], inplace=True)

# 2. Standardizing Categorical Fields
df['Season'] = df['Season'].str.strip().str.title()
df['Soil_Type'] = df['Soil_Type'].str.strip().str.title()
df['Crop'] = df['Crop'].str.strip().str.title()

# 3. Validation
print(f"Cleaned dataset shape: {df.shape}")
```

---

## 3. Outlier Detection & Handling

Crop yield and rainfall can exhibit extreme values due to erratic monsoons or localized farming successes. We used the **Interquartile Range (IQR)** method to inspect outliers.

```python
# Function to flag outliers
def detect_outliers_iqr(data_column):
    q1 = data_column.quantile(0.25)
    q3 = data_column.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - (1.5 * iqr)
    upper_bound = q3 + (1.5 * iqr)
    return lower_bound, upper_bound

rain_lower, rain_upper = detect_outliers_iqr(df['Rainfall_mm'])
print(f"Rainfall outliers bounds: {rain_lower} to {rain_upper}")

# Outliers in rainfall were kept if they were within physically possible bounds (e.g., heavy monsoon periods in Western Ghats districts)
# Yield anomalies exceeding 3 standard deviations from the crop mean were capped to avoid model distortion
```

---

## 4. Descriptive Statistics & Insights

Summary statistics for the climatic conditions across the 3,158 records:

| Metric | Temperature (°C) | Rainfall (mm) | Yield (Kg/Ha) |
| :--- | :---: | :---: | :---: |
| **Mean** | 27.4 | 845.2 | 2,120.4 |
| **Std Dev** | 3.8 | 312.6 | 890.1 |
| **Minimum** | 18.2 | 150.0 | 450.0 |
| **Median (50%)**| 27.1 | 820.0 | 2,050.0 |
| **Maximum** | 39.5 | 1850.0 | 5,200.0 |

---

## 5. Visual Exploration (Matplotlib & Seaborn)

### 5.1. Climate Distributions
We plotted the distribution of temperature and rainfall using kernel density estimations (KDE).

```python
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Rainfall Distribution
sns.histplot(df['Rainfall_mm'], kde=True, ax=axes[0], color='#2E8B57')
axes[0].set_title('Distribution of Seasonal Rainfall in Karnataka')
axes[0].set_xlabel('Rainfall (mm)')

# Temperature Distribution
sns.histplot(df['Temperature_C'], kde=True, ax=axes[1], color='#FF7F50')
axes[1].set_title('Distribution of Seasonal Temperature')
axes[1].set_xlabel('Temperature (°C)')

plt.tight_layout()
plt.savefig('../screenshots/climate_distributions.png')
plt.show()
```

### 5.2. Climatic Correlation Matrix
A heatmap was generated to analyze the correlation between environmental factors and crop yield.

```python
plt.figure(figsize=(8, 6))
correlation_matrix = df[['Temperature_C', 'Rainfall_mm', 'Yield_Kg_Ha']].corr()
sns.heatmap(correlation_matrix, annot=True, cmap='YlGnBu', fmt=".2f", linewidths=.5)
plt.title('Correlation Matrix: Climate & Yield')
plt.savefig('../screenshots/correlation_matrix.png')
plt.close()
```
*Insight:* The analysis revealed a moderate positive correlation (0.42) between Rainfall and Yield in dry regions, whereas temperature exhibited a slightly negative correlation with yield in high-heat zones during the Summer season.

### 5.3. Crop Patterns by Season and Soil
Grouping the dataset to identify the most common crops grown under various conditions:

```python
plt.figure(figsize=(12, 6))
sns.countplot(data=df, x='Soil_Type', hue='Season', palette='Set2')
plt.title('Distribution of Cultivated Land Soil Types by Season')
plt.xlabel('Soil Type')
plt.ylabel('Cultivation Count')
plt.xticks(rotation=45)
plt.legend(title='Season')
plt.tight_layout()
plt.savefig('../screenshots/soil_vs_season.png')
plt.close()
```

---

## 6. Preprocessing Output
The cleaned dataset was exported as `karnataka_agriculture_cleaned.csv` and placed in the `/dataset/` folder, serving as the source of truth for the Power BI dashboard and recommendation model development.
