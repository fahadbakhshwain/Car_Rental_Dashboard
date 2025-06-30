import datetime
import pandas as pd
import os

def run_weather_model_pipeline():
    print("--- Starting Weather Model Pipeline ---")

    # Define output directory and file path
    output_dir = "data/forecast_results"
    output_file_path = os.path.join(output_dir, "weather_forecast.csv")

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Get current time
    current_time = datetime.datetime.now()

    # Create a dummy forecast (replace with your actual weather model logic)
    weather_data = {
        "timestamp": [current_time],
        "location": ["Jeddah"],
        "temperature_celsius": [28.5 + (current_time.minute % 10) * 0.1], # A dummy fluctuating value
        "condition": ["Sunny"]
    }
    df_weather = pd.DataFrame(weather_data)

    # Save the forecast to a CSV file
    df_weather.to_csv(output_file_path, index=False)

    print(f"✅ Weather forecast generated successfully at: {current_time}")
    print(f"✅ Weather forecast saved to: {output_file_path}")
    print("--- Weather Model Pipeline Completed ---")

if __name__ == "__main__":
    run_weather_model_pipeline()