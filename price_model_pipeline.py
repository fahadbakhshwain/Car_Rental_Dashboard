import datetime
import pandas as pd
import os
import random

def run_price_model_pipeline():
    print("--- Starting Price Model Pipeline ---")

    # Define output directory and file path
    output_dir = "data/pricing_results"
    output_file_path = os.path.join(output_dir, "optimal_prices.csv")

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Get current time
    current_time = datetime.datetime.now()

    # Define some dummy data for pricing factors (replace with actual data loading/forecasting)
    car_categories = ['اقتصادية', 'سيدان', 'دفع رباعي', 'فان', 'فاخرة']
    rental_branches = ['المطار', 'وسط المدينة', 'الشمال', 'الجنوب', 'آخر']
    day_of_weeks = ['الاحد', 'الاثنين', 'الثلاثاء', 'الاربعاء', 'الخميس', 'الجمعة', 'السبت']

    # Generate dummy optimal prices (replace with your actual pricing model logic)
    pricing_data = []
    for category in car_categories:
        for branch in rental_branches:
            for day in day_of_weeks:
                base_price = 150 # Example base price
                # Simulate peak/off-peak pricing
                if day in ['الخميس', 'الجمعة', 'السبت']: # Weekend/peak days
                    suggested_price = base_price * (1 + random.uniform(0.1, 0.3)) # Increase by 10-30%
                else: # Weekdays/off-peak
                    suggested_price = base_price * (1 - random.uniform(0.05, 0.15)) # Decrease by 5-15%

                # Further adjustment based on category (dummy logic)
                if category == 'فاخرة': suggested_price *= 1.5
                elif category == 'دفع رباعي': suggested_price *= 1.2
                elif category == 'اقتصادية': suggested_price *= 0.8

                pricing_data.append({
                    "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "car_category": category,
                    "rental_branch": branch,
                    "day_of_week": day,
                    "suggested_price": round(suggested_price, 2)
                })

    df_prices = pd.DataFrame(pricing_data)

    # Save the optimal prices to a CSV file
    df_prices.to_csv(output_file_path, index=False)

    print(f"✅ Price model pipeline ran successfully at: {current_time}")
    print(f"✅ Optimal prices saved to: {output_file_path}")
    print("--- Price Model Pipeline Completed ---")

if __name__ == "__main__":
    run_price_model_pipeline()