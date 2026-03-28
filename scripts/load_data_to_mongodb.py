import csv
import json
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']

client = MongoClient(mongo_url)
db = client[db_name]

def load_aggregated_data():
    """Load historical data from aggregated_data.csv into MongoDB"""
    collection = db.historical_data
    collection.delete_many({})  # Clear existing data
    
    records = []
    with open('/app/data/aggregated_data.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            demand_drivers = json.loads(row['demand_drivers'])
            record = {
                'item_id': row['item_id'],
                'timestamp': row['timestamp'],
                'units_sold': int(row['units_sold']),
                'avg_unit_price': demand_drivers['avg_unit_price'],
                'cust_instock': demand_drivers['cust_instock']
            }
            records.append(record)
    
    if records:
        collection.insert_many(records)
    print(f"Loaded {len(records)} historical records into MongoDB")

def load_forecast_data():
    """Load forecast data from forecast_data.csv into MongoDB"""
    collection = db.forecasts
    collection.delete_many({})  # Clear existing data
    
    records = []
    with open('/app/data/forecast_data.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            forecasts = json.loads(row['forecasts'])
            demand_drivers = json.loads(row['demand_drivers'])
            
            record = {
                'item_id': row['item_id'],
                'inference_date': row['inference_date'],
                'forecasts': forecasts,
                'demand_drivers': demand_drivers,
                'model_id': row['model_id'],
                'run_id': row['run_id'],
                'client_id': row['client_id']
            }
            records.append(record)
    
    if records:
        collection.insert_many(records)
    print(f"Loaded {len(records)} forecast records into MongoDB")

if __name__ == "__main__":
    print("Loading data into MongoDB...")
    load_aggregated_data()
    load_forecast_data()
    print("Data loading complete!")
    client.close()
