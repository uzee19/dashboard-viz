from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")

# Models
class HistoricalData(BaseModel):
    model_config = ConfigDict(extra="ignore")
    item_id: str
    timestamp: str
    units_sold: int
    avg_unit_price: float
    cust_instock: float

class ForecastPoint(BaseModel):
    timestamp: str
    values: Dict[str, Any]

class DemandDriver(BaseModel):
    timestamp: str
    avg_unit_price: float
    cust_instock: float

class ForecastData(BaseModel):
    model_config = ConfigDict(extra="ignore")
    item_id: str
    inference_date: str
    forecasts: List[Dict[str, Any]]
    demand_drivers: List[Dict[str, Any]]

class SKUListItem(BaseModel):
    item_id: str

class AlertItem(BaseModel):
    item_id: str
    severity: str
    message: str
    deviation_percent: float

@api_router.get("/")
async def root():
    return {"message": "Demand Planning Dashboard API"}

@api_router.get("/skus", response_model=List[SKUListItem])
async def get_all_skus():
    """Get all unique SKU IDs"""
    skus = await db.historical_data.distinct("item_id")
    return [{"item_id": sku} for sku in sorted(skus)]

@api_router.get("/home-data")
async def get_home_data():
    """Get aggregated data for home page (last 13 weeks historical + 39 weeks forecast)"""
    # Get all historical data
    historical = await db.historical_data.find({}, {"_id": 0}).to_list(1000)
    
    # Group by timestamp and sum units_sold
    from collections import defaultdict
    weekly_totals = defaultdict(int)
    
    for record in historical:
        weekly_totals[record['timestamp']] += record['units_sold']
    
    # Sort by timestamp and get last 13 weeks
    sorted_weeks = sorted(weekly_totals.items(), key=lambda x: x[0])
    last_13_weeks = sorted_weeks[-13:] if len(sorted_weeks) >= 13 else sorted_weeks
    
    historical_chart_data = [
        {"timestamp": week, "units_sold": total, "type": "historical"}
        for week, total in last_13_weeks
    ]
    
    # Get forecast data (aggregate across all SKUs)
    forecasts = await db.forecasts.find({}, {"_id": 0}).to_list(100)
    
    forecast_weekly_totals = defaultdict(int)
    for forecast_record in forecasts:
        for forecast_point in forecast_record['forecasts'][:39]:  # Next 39 weeks
            forecast_weekly_totals[forecast_point['timestamp']] += forecast_point['values']['mean']
    
    forecast_chart_data = [
        {"timestamp": week, "units_sold": int(total), "type": "forecast"}
        for week, total in sorted(forecast_weekly_totals.items())
    ]
    
    return {
        "chart_data": historical_chart_data + forecast_chart_data
    }

@api_router.get("/alerts", response_model=List[AlertItem])
async def get_alerts():
    """Get SKUs that need attention based on forecast accuracy"""
    alerts = []
    
    # Get all SKUs
    skus = await db.historical_data.distinct("item_id")
    
    for sku in skus:
        # Get recent historical data (last 3 weeks)
        historical = await db.historical_data.find(
            {"item_id": sku},
            {"_id": 0}
        ).sort("timestamp", -1).limit(3).to_list(3)
        
        if len(historical) < 3:
            continue
        
        avg_historical = sum(h['units_sold'] for h in historical) / len(historical)
        
        # Get forecast data
        forecast = await db.forecasts.find_one({"item_id": sku}, {"_id": 0})
        
        if not forecast or not forecast.get('forecasts'):
            continue
        
        # Get first 3 weeks of forecast
        first_3_forecasts = forecast['forecasts'][:3]
        avg_forecast = sum(f['values']['mean'] for f in first_3_forecasts) / len(first_3_forecasts)
        
        # Calculate deviation
        if avg_historical > 0:
            deviation = ((avg_forecast - avg_historical) / avg_historical) * 100
            
            # Alert if deviation is significant
            if abs(deviation) > 20:
                severity = "high" if abs(deviation) > 40 else "medium"
                direction = "increase" if deviation > 0 else "decrease"
                
                alerts.append({
                    "item_id": sku,
                    "severity": severity,
                    "message": f"Forecast shows {abs(deviation):.1f}% {direction} from recent trends",
                    "deviation_percent": round(deviation, 2)
                })
    
    # Sort by severity (high first) and deviation
    alerts.sort(key=lambda x: (0 if x['severity'] == 'high' else 1, -abs(x['deviation_percent'])))
    
    return alerts[:10]  # Return top 10 alerts

@api_router.get("/sku/{item_id}")
async def get_sku_detail(item_id: str):
    """Get detailed data for a specific SKU"""
    # Get historical data
    historical = await db.historical_data.find(
        {"item_id": item_id},
        {"_id": 0}
    ).sort("timestamp", 1).to_list(100)
    
    if not historical:
        raise HTTPException(status_code=404, detail="SKU not found")
    
    # Get last 13 weeks
    last_13_weeks = historical[-13:] if len(historical) >= 13 else historical
    
    historical_chart_data = [
        {
            "timestamp": h['timestamp'],
            "units_sold": h['units_sold'],
            "type": "historical"
        }
        for h in last_13_weeks
    ]
    
    # Get forecast data
    forecast = await db.forecasts.find_one({"item_id": item_id}, {"_id": 0})
    
    if not forecast:
        return {
            "item_id": item_id,
            "chart_data": historical_chart_data,
            "forecast_data": []
        }
    
    # Get next 39 weeks of forecast
    forecast_chart_data = [
        {
            "timestamp": f['timestamp'],
            "units_sold": f['values']['mean'],
            "p05": f['values']['p05'],
            "p95": f['values']['p95'],
            "type": "forecast"
        }
        for f in forecast['forecasts'][:39]
    ]
    
    return {
        "item_id": item_id,
        "chart_data": historical_chart_data + forecast_chart_data
    }

@api_router.get("/sku/{item_id}/demand-drivers")
async def get_demand_drivers(item_id: str):
    """Get demand drivers (historical + projected) for a specific SKU"""
    # Get historical demand drivers
    historical = await db.historical_data.find(
        {"item_id": item_id},
        {"_id": 0}
    ).sort("timestamp", 1).to_list(100)
    
    if not historical:
        raise HTTPException(status_code=404, detail="SKU not found")
    
    # Get last 13 weeks
    last_13_weeks = historical[-13:] if len(historical) >= 13 else historical
    
    historical_drivers = [
        {
            "timestamp": h['timestamp'],
            "avg_unit_price": h['avg_unit_price'],
            "cust_instock": h['cust_instock'],
            "type": "historical"
        }
        for h in last_13_weeks
    ]
    
    # Get forecasted demand drivers
    forecast = await db.forecasts.find_one({"item_id": item_id}, {"_id": 0})
    
    forecast_drivers = []
    if forecast and forecast.get('demand_drivers'):
        forecast_drivers = [
            {
                "timestamp": d['timestamp'],
                "avg_unit_price": d['avg_unit_price'],
                "cust_instock": d['cust_instock'],
                "type": "forecast"
            }
            for d in forecast['demand_drivers'][:39]
        ]
    
    return {
        "item_id": item_id,
        "demand_drivers": historical_drivers + forecast_drivers
    }

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
