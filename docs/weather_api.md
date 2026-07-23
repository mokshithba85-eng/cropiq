# Weather API Integration Methodology

This document outlines the design and implementation of the live weather REST API integration within the **CropIQ Power BI Dashboard** using Power Query M Language.

---

## 1. Integration Architecture

To provide real-time decision support, the dashboard requests live climatic conditions from a weather service and displays them side-by-side with historical trends.

```
+------------------------+      API Key      +-------------------------+
|      Power Query       |  +------------->  |   OpenWeatherMap API    |
|   (M Engine Query)     |  <-------------+  |  (REST API Weather Data)|
+-----------+------------+   JSON Response   +-------------------------+
            |
            v
+-----------+------------+
|   District Weather     |
|   Table (Expanded)     |
+-----------+------------+
            |
            | (Relationship: 1 to Many on District Name)
            v
+-----------+------------+
|   Historical dataset   |
|     (3,158 records)    |
+------------------------+
```

---

## 2. Power Query (M Language) Implementation

Direct API calls in Power Query that use concatenated strings often fail scheduled refreshes on Power BI Service due to security/privacy evaluations of dynamic data sources. To bypass this, we implemented the query using `RelativePath` and `Query` arguments in `Web.Contents`.

### Power Query M Code
```powerquery
let
    // 1. Fetch API Key and Target Districts parameters
    API_Key = #"Weather_API_Key_Parameter",
    Selected_District = #"Target_District_Parameter", // or reference District column in table
    
    // 2. Formulate HTTP request using Web.Contents with RelativePath
    Source = Web.Contents(
        "https://api.openweathermap.org",
        [
            RelativePath = "data/2.5/weather",
            Query = [
                q = Selected_District & ",IN", // Appends India country code
                appid = API_Key,
                units = "metric"
            ]
        ]
    ),
    
    // 3. Parse JSON Response
    JSON_Response = Json.Document(Source),
    
    // 4. Extract target parameters
    coord = JSON_Response[coord],
    lon = coord[lon],
    lat = coord[lat],
    
    weather = JSON_Response[weather]{0},
    weather_main = weather[main],
    weather_desc = weather[description],
    
    main = JSON_Response[main],
    temp = main[temp],
    humidity = main[humidity],
    pressure = main[pressure],
    
    wind = JSON_Response[wind],
    wind_speed = wind[speed],
    
    // 5. Convert record to a table structure
    WeatherTable = Table.FromRecords({[
        District = Selected_District,
        Latitude = lat,
        Longitude = lon,
        Current_Temperature = temp,
        Humidity_Percent = humidity,
        Pressure_hPa = pressure,
        Wind_Speed_m_s = wind_speed,
        Weather_Condition = weather_main,
        Weather_Description = weather_desc,
        Last_Updated = DateTime.LocalNow()
    ]})
in
    WeatherTable
```

---

## 3. Power BI Service Scheduled Refresh Configuration

Setting up a REST API connection within a Power BI report requires extra care when publishing to the Power BI Service:

1. **Parameters Configuration:**
   - Define a Power BI parameter `Weather_API_Key_Parameter` with a default key value. This prevents the API key from being hardcoded directly into the M script and allows developers to change keys in the Service settings without modifying the `.pbix` file.
2. **Anonymous / Web Credentials:**
   - When publishing to Power BI Service, navigate to **Dataset Settings -> Data source credentials**.
   - Edit the credentials for the weather endpoint, set the authentication method to **Anonymous** (since the API key is passed in the query parameters of the request, not via HTTP headers).
3. **Gateway Requirements:**
   - Since the weather data source is a cloud-based REST API, a local On-Premises Data Gateway is **not** required. Power BI Service refreshes the API connection directly from the cloud.
4. **Refresh Schedule:**
   - Configured to refresh 4 times daily (e.g., 6:00 AM, 12:00 PM, 4:00 PM, 8:00 PM) to capture changing weather patterns during key farming periods.

---

## 4. API Limitations & Error Handling

To make the integration production-ready, the M query includes defensive code to handle network drops and API limit errors:

- **Empty Responses (HTTP 404/500):** Wrapped with a try/otherwise block:
  ```powerquery
  try JSON_Response[main][temp] otherwise null
  ```
- **Call Quota (HTTP 429):** The standard free tier of OpenWeatherMap permits 60 calls per minute. To prevent exceeding limits during refresh, the query runs on a list of unique districts (max 30 in Karnataka) rather than making calls for each of the 3,158 records. It is then merged with the primary dataset inside Power BI relationships using the `District` column.
