import csv
import json
from datetime import datetime, timedelta
import random

# Generate mock data for aggregated_data.csv and forecast_data.csv

def generate_mock_data():
    # Configuration
    num_skus = 15
    historical_weeks = 13
    forecast_weeks = 40
    current_date = datetime(2025, 4, 20)
    inference_date = datetime(2025, 4, 20)
    
    # Generate SKU IDs
    sku_ids = [f"CUST_003_ITEM_{str(i).zfill(4)}" for i in range(1, num_skus + 1)]
    
    # Generate aggregated_data.csv
    aggregated_data = []
    for sku in sku_ids:
        base_units = random.randint(500, 2000)
        base_price = round(random.uniform(10, 100), 2)
        
        for week in range(historical_weeks):
            week_date = current_date - timedelta(weeks=historical_weeks - week - 1)
            units_sold = max(0, base_units + random.randint(-200, 300))
            avg_price = round(base_price + random.uniform(-5, 5), 2)
            instock = round(random.uniform(0.7, 1.0), 3)
            
            demand_drivers = {
                "avg_unit_price": avg_price,
                "cust_instock": instock
            }
            
            aggregated_data.append({
                "item_id": sku,
                "timestamp": week_date.strftime("%Y-%m-%d"),
                "units_sold": units_sold,
                "demand_drivers": json.dumps(demand_drivers)
            })
    
    # Write aggregated_data.csv
    with open('/app/data/aggregated_data.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['item_id', 'timestamp', 'units_sold', 'demand_drivers'])
        writer.writeheader()
        writer.writerows(aggregated_data)
    
    print(f"Created aggregated_data.csv with {len(aggregated_data)} records")
    
    # Generate forecast_data.csv
    forecast_data = []
    for sku in sku_ids:
        base_forecast = random.randint(500, 2000)
        base_price = round(random.uniform(10, 100), 2)
        
        forecasts = []
        demand_drivers_forecast = []
        
        for week in range(forecast_weeks):
            week_date = current_date + timedelta(weeks=week + 1)
            mean_forecast = max(0, base_forecast + random.randint(-150, 250))
            
            forecast_entry = {
                "timestamp": week_date.strftime("%Y-%m-%d"),
                "values": {
                    "mean": mean_forecast,
                    "p05": int(mean_forecast * 0.7),
                    "p10": int(mean_forecast * 0.75),
                    "p25": int(mean_forecast * 0.85),
                    "p50": mean_forecast,
                    "p75": int(mean_forecast * 1.15),
                    "p90": int(mean_forecast * 1.25),
                    "p95": int(mean_forecast * 1.30)
                }
            }
            forecasts.append(forecast_entry)
            
            avg_price = round(base_price + random.uniform(-3, 3), 2)
            instock = round(random.uniform(0.75, 0.95), 3)
            
            demand_drivers_forecast.append({
                "timestamp": week_date.strftime("%Y-%m-%d"),
                "avg_unit_price": avg_price,
                "cust_instock": instock
            })
        
        forecast_data.append({
            "item_id": sku,
            "inference_date": inference_date.strftime("%Y-%m-%d"),
            "forecasts": json.dumps(forecasts),
            "demand_drivers": json.dumps(demand_drivers_forecast),
            "model_id": "model_v2.1",
            "run_id": f"run_{random.randint(1000, 9999)}",
            "client_id": "CUST_003"
        })
    
    # Write forecast_data.csv
    with open('/app/data/forecast_data.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['item_id', 'inference_date', 'forecasts', 'demand_drivers', 'model_id', 'run_id', 'client_id'])
        writer.writeheader()
        writer.writerows(forecast_data)
    
    print(f"Created forecast_data.csv with {len(forecast_data)} records")

if __name__ == "__main__":
    import os
    os.makedirs('/app/data', exist_ok=True)
    generate_mock_data()
    print("Mock data generation complete!")
