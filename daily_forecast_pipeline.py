import datetime
import pandas as pd
import os
import requests # أضفنا هذا الاستيراد لإجراء طلبات الـ API

def run_weather_model_pipeline():
    print("--- Starting Weather Model Pipeline ---")

    # Define API key and city
    api_key = os.environ.get("OPENWEATHER_API_KEY") # قراءة مفتاح API من متغيرات البيئة
    city_name = "Jeddah"
    
    if not api_key:
        print("❌ Error: OPENWEATHER_API_KEY environment variable not set. Cannot fetch real weather data.")
        print("Using dummy weather data for now.")
        # Fallback to dummy data if API key is not set (for local testing without API key)
        current_time = datetime.datetime.now()
        weather_data = {
            "timestamp": [current_time],
            "location": [city_name],
            "temperature_celsius": [25.0], # Fallback value
            "condition": ["Unknown"]
        }
    else:
        # Construct API URL for current weather data
        # Using 'weather' endpoint for current data, or 'forecast' for future
        # For simplicity, we'll use current weather for a daily snapshot
        api_url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric"
        
        print(f"Fetching weather data for {city_name} from OpenWeatherMap API...")
        try:
            response = requests.get(api_url)
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            weather_json = response.json()

            current_time = datetime.datetime.now()
            temperature = weather_json['main']['temp']
            condition = weather_json['weather'][0]['description']
            
            weather_data = {
                "timestamp": [current_time],
                "location": [city_name],
                "temperature_celsius": [temperature],
                "condition": [condition]
            }
            print("✅ Weather data fetched successfully from OpenWeatherMap API!")

        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching weather data from API: {e}")
            print("Using dummy weather data as a fallback due to API error.")
            current_time = datetime.datetime.now()
            weather_data = {
                "timestamp": [current_time],
                "location": [city_name],
                "temperature_celsius": [25.0], # Fallback value
                "condition": ["API Error / Unknown"]
            }
        except KeyError as e:
            print(f"❌ Error parsing API response: Missing key {e}. Response: {weather_json}")
            print("Using dummy weather data as a fallback due to parsing error.")
            current_time = datetime.datetime.now()
            weather_data = {
                "timestamp": [current_time],
                "location": [city_name],
                "temperature_celsius": [25.0], # Fallback value
                "condition": ["Parsing Error / Unknown"]
            }

    # Define output directory and file path
    output_dir = "data/forecast_results"
    output_file_path = os.path.join(output_dir, "weather_forecast.csv")
    os.makedirs(output_dir, exist_ok=True) # Ensure the output directory exists

    # Create DataFrame and save to CSV
    df_weather = pd.DataFrame(weather_data)
    df_weather.to_csv(output_file_path, index=False)

    print(f"✅ Weather forecast saved to: {output_file_path}")
    print("--- Weather Model Pipeline Completed ---")

if __name__ == "__main__":
    run_weather_model_pipeline()