# DAX Logic & Analytical Measures

This document outlines the Data Analysis Expressions (DAX) developed in Power BI to power the KPIs, dynamic visualizations, and crop suitability metrics.

---

## 1. Core Agricultural KPI Measures

These measures calculate the standard baseline figures shown in the dashboard's summary cards.

### Total Cultivation Records
Counts the active data rows, representing total reported crop cycles in the 3,158-record dataset.
```dax
Total_Records = COUNTROWS('Karnataka_Agriculture')
```

### Average Yield (Kg/Ha)
Calculates the average crop productivity per unit of land.
```dax
Average_Yield = AVERAGE('Karnataka_Agriculture'[Yield_Kg_Ha])
```

### Total Production (Tons)
Calculates the total agricultural output by assuming a constant cultivated land size (in hectares) for yield calculation.
```dax
Total_Production_Tons = 
SUMX(
    'Karnataka_Agriculture',
    ('Karnataka_Agriculture'[Yield_Kg_Ha] * 'Karnataka_Agriculture'[Area_Hectares]) / 1000
)
```
*(Note: If Area is a variable in the dataset, this computes the absolute crop volume in metric tons).*

---

## 2. Climatic Indicators & Deviations

These formulas evaluate climate deviations to provide warnings when conditions deviate from seasonal norms.

### Rainfall Deviation
Computes the percentage deviation of a district's selected rainfall against the historical statewide seasonal average.
```dax
Rainfall_Deviation = 
VAR DistrictRain = AVERAGE('Karnataka_Agriculture'[Rainfall_mm])
VAR StateAverageRain = 
    CALCULATE(
        AVERAGE('Karnataka_Agriculture'[Rainfall_mm]),
        ALL('Karnataka_Agriculture'[District])
    )
RETURN
    DIVIDE(DistrictRain - StateAverageRain, StateAverageRain, 0)
```

### Temperature Status (Alert)
Returns a text label indicating weather stress based on average temperatures.
```dax
Temperature_Status = 
VAR AvgTemp = AVERAGE('Karnataka_Agriculture'[Temperature_C])
RETURN
    SWITCH(
        TRUE(),
        AvgTemp >= 35, "Heat Stress Risk",
        AvgTemp < 20, "Frost/Chill Stress Risk",
        "Optimal Range"
    )
```

---

## 3. Crop Recommendation Logic (DAX-Based Engine)

The crop recommendation engine recommends suitable crop categories based on environmental inputs: Soil Type, Rainfall, Temperature, and Season.

### Suitable Crop Recommendation Metric
This measure evaluates conditions and outputs a suitability score or list of recommended crops.

```dax
Recommended_Crop_Category = 
VAR SelectedSoil = SELECTEDVALUE('Karnataka_Agriculture'[Soil_Type], "Red")
VAR SelectedSeason = SELECTEDVALUE('Karnataka_Agriculture'[Season], "Kharif")
VAR AvgRain = [Average_Rainfall_mm]  -- References another average measure
VAR AvgTemp = [Average_Temperature_C]

RETURN
    SWITCH(
        TRUE(),
        -- Kharif crops (High Rainfall, Moderate to High Temp)
        SelectedSeason = "Kharif" && SelectedSoil = "Black" && AvgRain >= 800 && AvgTemp >= 25, "Cotton / Paddy",
        SelectedSeason = "Kharif" && SelectedSoil = "Red" && AvgRain >= 600 && AvgTemp >= 24, "Maize / Groundnut",
        
        -- Rabi crops (Moderate Rainfall, Cooler Temp)
        SelectedSeason = "Rabi" && SelectedSoil = "Black" && AvgRain <= 500 && AvgTemp <= 24, "Wheat / Jowar",
        SelectedSeason = "Rabi" && SelectedSoil = "Red" && AvgRain <= 450 && AvgTemp <= 25, "Bengal Gram",
        
        -- Summer crops (Low Rainfall, High Temp, Clayey/Sandy Soils with Irrigation)
        SelectedSeason = "Summer" && AvgTemp >= 28 && AvgRain <= 300, "Pulses (Moong/Urad) / Millets",
        
        -- Fallback
        "Short-duration Millets / Fodder Crops"
    )
```

---

## 4. Conditional Formatting & Dynamic KPI Colors

To implement premium UI aesthetics, dynamic visual styling was configured using hex codes generated via DAX.

### KPI Color Flag (Yield Performance)
Changes the background or text color of cards depending on how a selected district's average yield performs compared to the overall state average.
```dax
Yield_KPI_Color = 
VAR CurrentYield = [Average_Yield]
VAR StateAverageYield = 
    CALCULATE(
        AVERAGE('Karnataka_Agriculture'[Yield_Kg_Ha]),
        ALL('Karnataka_Agriculture')
    )
RETURN
    IF(
        CurrentYield >= StateAverageYield, 
        "#2E8B57",  -- Green (Good Performance)
        "#D9534F"   -- Soft Red (Underperforming)
    )
```

### Weather Alert Color Code
Assigns colors to live weather indicators:
```dax
Weather_Alert_Color = 
VAR AvgTemp = AVERAGE('Karnataka_Agriculture'[Temperature_C])
RETURN
    SWITCH(
        TRUE(),
        AvgTemp >= 35, "#FF8C00",  -- Dark Orange (Hot)
        AvgTemp <= 20, "#4682B4",  -- Steel Blue (Cool)
        "#2E8B57"                  -- Sea Green (Optimal)
    )
```
*(These dynamic measures are bound to the "FX" conditional formatting settings of cards and visuals in the Power BI dashboard).*
