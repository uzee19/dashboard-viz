# Demand Planning Dashboard

A full-stack web application for retail supply chain teams to monitor weekly sales performance and review AI-generated forecasts at SKU (Stock Keeping Unit) level.


## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Database Schema](#database-schema)
- [API Documentation](#api-documentation)
- [Frontend Structure](#frontend-structure)
- [Data Flow](#data-flow)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Project Structure](#project-structure)

---

## 🎯 Overview

The Demand Planning Dashboard is designed to help supply chain professionals:
- Monitor weekly sales performance across multiple SKUs
- Review AI-generated demand forecasts
- Identify items requiring attention based on forecast accuracy
- Analyze demand drivers (pricing and inventory factors)
- Make data-driven inventory and planning decisions

The dashboard provides a 52-week view (13 weeks historical + 39 weeks forecast) with intelligent alerting for anomalies.

---

## ✨ Features

### Home Dashboard
- **Aggregated Sales Chart**: Visualizes total units sold across all SKUs for 52 weeks
- **Forecast Alerts**: Displays high/medium priority alerts for SKUs with significant forecast deviations (>20% from recent trends)
- **SKU Search**: Quick search functionality to navigate to specific SKU details
- **Quick Access**: Grid of all available SKUs for easy navigation

### SKU Detail Workbench
- **52-Week Forecast Chart**: Individual SKU performance with historical actuals and AI forecasts
- **Demand Drivers Panel**: Toggle-able side panel showing:
  - Average Unit Price trends (historical + projected)
  - Customer In-Stock Rate trends (historical + projected)
- **Visual Indicators**: Clear separation between historical data and forecasts
- **Interactive Charts**: Hover tooltips with detailed data points

### Alert System
- **Smart Detection**: Automatically identifies SKUs where forecasts deviate significantly from recent trends
- **Priority Levels**:
  - **High Priority** (>40% deviation): Red border and icon
  - **Medium Priority** (20-40% deviation): Yellow border and icon
- **Actionable**: Click any alert to navigate directly to SKU detail page

---

## 🛠 Tech Stack

### Frontend
- **Framework**: React 19.0.0
- **Routing**: React Router DOM v7.5.1
- **Charts**: Recharts v3.6.0
- **Styling**: Tailwind CSS v3.4.17
- **Animations**: Framer Motion v12.38.0
- **Icons**: Phosphor Icons React v2.1.10
- **HTTP Client**: Axios v1.8.4
- **UI Components**: Radix UI (shadcn/ui components)

### Backend
- **Framework**: FastAPI 0.110.1
- **Server**: Uvicorn 0.25.0
- **Database Driver**: Motor (AsyncIO MongoDB) 3.3.1
- **Database**: MongoDB (local instance)
- **Data Processing**: Pandas 2.2.0, NumPy 1.26.0
- **Environment**: Python 3.x with python-dotenv

### Development Tools
- **Package Manager**: Yarn 1.22.22 (Frontend), pip (Backend)
- **Process Manager**: Supervisor
- **Linting**: ESLint (Frontend), Ruff (Backend)

---

## 🏗 Architecture

### High-Level Architecture

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │         │                 │
│  React Frontend │ ◄─────► │  FastAPI Backend│ ◄─────► │    MongoDB      │
│   (Port 3000)   │  HTTP   │   (Port 8001)   │  Motor  │  (Port 27017)   │
│                 │         │                 │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
        │                           │
        │                           │
        ▼                           ▼
   Recharts                    Collections:
   Visualizations              - historical_data
                               - forecasts
```

### Data Architecture

```
CSV Files (Mock Data)
    │
    ├── aggregated_data.csv (195 records)
    │   └── 15 SKUs × 13 weeks historical data
    │
    └── forecast_data.csv (15 records)
        └── 15 SKUs × 40 weeks forecast data
              │
              ▼
    Data Loading Scripts
    (scripts/create_mock_data.py)
    (scripts/load_data_to_mongodb.py)
              │
              ▼
         MongoDB
    ┌─────────────────────┐
    │ historical_data     │
    │ - item_id           │
    │ - timestamp         │
    │ - units_sold        │
    │ - avg_unit_price    │
    │ - cust_instock      │
    └─────────────────────┘
    ┌─────────────────────┐
    │ forecasts           │
    │ - item_id           │
    │ - inference_date    │
    │ - forecasts[]       │
    │ - demand_drivers[]  │
    └─────────────────────┘
```

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** >= 16.x
- **Python** >= 3.8
- **MongoDB** >= 4.x (running locally)
- **Yarn** package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd demand-planning-dashboard
   ```

2. **Backend Setup**
   ```bash
   cd backend
   
   # Install Python dependencies
   pip install -r requirements.txt
   
   # Configure environment variables
   # The .env file should already contain:
   # MONGO_URL="mongodb://localhost:27017"
   # DB_NAME="test_database"
   # CORS_ORIGINS="*"
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   
   # Install Node dependencies
   yarn install
   
   # The .env file should contain:
   # REACT_APP_BACKEND_URL=<your-backend-url>
   # WDS_SOCKET_PORT=443
   # ENABLE_HEALTH_CHECK=false
   ```

4. **Generate and Load Mock Data**
   ```bash
   # From project root
   python scripts/create_mock_data.py
   python scripts/load_data_to_mongodb.py
   ```

### Running the Application

#### Development Mode (using Supervisor)

```bash
# Start backend
sudo supervisorctl start backend

# Start frontend
sudo supervisorctl start frontend

# Check status
sudo supervisorctl status
```

#### Manual Mode

**Backend:**
```bash
cd backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

**Frontend:**
```bash
cd frontend
yarn start
```

The application will be available at:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8001`
- API Documentation: `http://localhost:8001/docs`

---

## 🗄 Database Schema

### Collection: `historical_data`

Stores weekly historical sales actuals per SKU.

| Field            | Type    | Description                           |
|------------------|---------|---------------------------------------|
| item_id          | String  | Unique SKU identifier                 |
| timestamp        | String  | Week start date (YYYY-MM-DD)          |
| units_sold       | Integer | Actual units sold that week           |
| avg_unit_price   | Float   | Average selling price that week       |
| cust_instock     | Float   | Customer in-stock rate (0.0 - 1.0)    |

**Example Document:**
```json
{
  "item_id": "CUST_003_ITEM_0001",
  "timestamp": "2025-02-02",
  "units_sold": 1547,
  "avg_unit_price": 78.45,
  "cust_instock": 0.892
}
```

**Indexes:**
- `item_id` (for SKU lookups)
- `timestamp` (for time-series queries)

---

### Collection: `forecasts`

Stores AI-generated forecast data per SKU.

| Field            | Type   | Description                                      |
|------------------|--------|--------------------------------------------------|
| item_id          | String | Unique SKU identifier                            |
| inference_date   | String | Date the forecast was generated                  |
| forecasts        | Array  | Array of 40 weekly forecast objects             |
| demand_drivers   | Array  | Array of 40 weekly demand driver projections    |
| model_id         | String | Model version identifier                         |
| run_id           | String | Forecast run identifier                          |
| client_id        | String | Client identifier                                |

**Forecast Object Structure:**
```json
{
  "timestamp": "2025-04-27",
  "values": {
    "mean": 1650,
    "p05": 1155,
    "p10": 1237,
    "p25": 1402,
    "p50": 1650,
    "p75": 1897,
    "p90": 2062,
    "p95": 2145
  }
}
```

**Demand Driver Object Structure:**
```json
{
  "timestamp": "2025-04-27",
  "avg_unit_price": 75.30,
  "cust_instock": 0.85
}
```

**Example Document:**
```json
{
  "item_id": "CUST_003_ITEM_0001",
  "inference_date": "2025-04-20",
  "forecasts": [
    {
      "timestamp": "2025-04-27",
      "values": {
        "mean": 1650,
        "p05": 1155,
        "p50": 1650,
        "p95": 2145
      }
    }
    // ... 39 more forecast objects
  ],
  "demand_drivers": [
    {
      "timestamp": "2025-04-27",
      "avg_unit_price": 75.30,
      "cust_instock": 0.85
    }
    // ... 39 more driver objects
  ],
  "model_id": "model_v2.1",
  "run_id": "run_5432",
  "client_id": "CUST_003"
}
```

**Indexes:**
- `item_id` (for SKU lookups)
- `inference_date` (to fetch latest forecasts)

---

## 📡 API Documentation

All API endpoints are prefixed with `/api`.

### Base URL
- Development: `http://localhost:8001/api`
- Production: `https://<your-domain>/api`

---

### `GET /api/`

**Description:** API health check

**Response:**
```json
{
  "message": "Demand Planning Dashboard API"
}
```

---

### `GET /api/skus`

**Description:** Get all unique SKU identifiers

**Response:**
```json
[
  { "item_id": "CUST_003_ITEM_0001" },
  { "item_id": "CUST_003_ITEM_0002" },
  ...
]
```

**Use Case:** Populate SKU selection dropdowns, quick access lists

---

### `GET /api/home-data`

**Description:** Get aggregated sales data for home page dashboard (last 13 weeks historical + 39 weeks forecast)

**Response:**
```json
{
  "chart_data": [
    {
      "timestamp": "2025-02-02",
      "units_sold": 18450,
      "type": "historical"
    },
    {
      "timestamp": "2025-04-27",
      "units_sold": 17820,
      "type": "forecast"
    },
    ...
  ]
}
```

**Data Points:** 52 total (13 historical + 39 forecast)

**Use Case:** Main dashboard overview chart

---

### `GET /api/alerts`

**Description:** Get SKUs requiring attention based on forecast accuracy

**Algorithm:**
- Compares average of last 3 weeks historical vs. first 3 weeks forecast
- Flags SKUs with >20% deviation
- Returns top 10 alerts sorted by severity and deviation

**Response:**
```json
[
  {
    "item_id": "CUST_003_ITEM_0001",
    "severity": "high",
    "message": "Forecast shows 66.9% increase from recent trends",
    "deviation_percent": 66.94
  },
  {
    "item_id": "CUST_003_ITEM_0010",
    "severity": "medium",
    "message": "Forecast shows 32.1% decrease from recent trends",
    "deviation_percent": -32.1
  },
  ...
]
```

**Severity Levels:**
- `high`: |deviation| > 40%
- `medium`: 20% < |deviation| <= 40%

**Use Case:** Alert cards on home page

---

### `GET /api/sku/{item_id}`

**Description:** Get detailed historical and forecast data for a specific SKU

**Path Parameters:**
- `item_id` (required): SKU identifier (e.g., "CUST_003_ITEM_0001")

**Response:**
```json
{
  "item_id": "CUST_003_ITEM_0001",
  "chart_data": [
    {
      "timestamp": "2025-02-02",
      "units_sold": 1547,
      "type": "historical"
    },
    {
      "timestamp": "2025-04-27",
      "units_sold": 1650,
      "p05": 1155,
      "p95": 2145,
      "type": "forecast"
    },
    ...
  ]
}
```

**Data Points:** 52 total (13 historical + 39 forecast)

**Error Response (404):**
```json
{
  "detail": "SKU not found"
}
```

**Use Case:** SKU detail workbench main chart

---

### `GET /api/sku/{item_id}/demand-drivers`

**Description:** Get demand driver data (historical actuals + projected) for a specific SKU

**Path Parameters:**
- `item_id` (required): SKU identifier

**Response:**
```json
{
  "item_id": "CUST_003_ITEM_0001",
  "demand_drivers": [
    {
      "timestamp": "2025-02-02",
      "avg_unit_price": 78.45,
      "cust_instock": 0.892,
      "type": "historical"
    },
    {
      "timestamp": "2025-04-27",
      "avg_unit_price": 75.30,
      "cust_instock": 0.85,
      "type": "forecast"
    },
    ...
  ]
}
```

**Data Points:** 52 total (13 historical + 39 forecast)

**Use Case:** Demand drivers side panel charts

---

## 🎨 Frontend Structure

### Pages

#### Home (`/app/frontend/src/pages/Home.js`)
- **Route:** `/`
- **Components:**
  - Header with logo and search bar
  - Aggregated 52-week sales chart
  - Forecast alerts grid (3 columns)
  - Quick SKU access grid (5 columns)

#### SKU Detail (`/app/frontend/src/pages/SKUDetail.js`)
- **Route:** `/sku/:itemId`
- **Components:**
  - Header with back button and logo
  - 52-week forecast chart (main)
  - Toggleable demand drivers side panel
    - Average Unit Price chart
    - Customer In-Stock Rate chart

### Design System

**Design Philosophy:** Swiss & High-Contrast

**Typography:**
- **Headings:** Chivo (Black 900, Bold 700)
- **Body:** IBM Plex Sans (Regular 400, Medium 500)

**Color Palette:**
```css
--background: #FFFFFF
--foreground: #09090B
--border: #E4E4E7
--muted-background: #F4F4F5
--muted-foreground: #71717A

/* Alert Colors */
--alert-high: #E11D48 (Red)
--alert-medium: #FACC15 (Yellow)

/* Chart Colors */
--chart-primary: #2563EB (Blue)
--chart-success: #10B981 (Green)
--chart-danger: #E11D48 (Red)
```

**Layout Principles:**
- Sharp borders (1px solid, border-radius max 2px)
- Minimal shadows (none on most elements)
- High contrast for accessibility
- Ample whitespace (gap-4 to gap-6)

### State Management

React hooks are used for state management:
- `useState` for local component state
- `useEffect` for data fetching
- `useNavigate` for programmatic navigation
- `useParams` for route parameters

### Data Fetching Pattern

```javascript
const [data, setData] = useState([]);
const [loading, setLoading] = useState(true);

useEffect(() => {
  const fetchData = async () => {
    try {
      const response = await axios.get(`${API}/endpoint`);
      setData(response.data);
      setLoading(false);
    } catch (e) {
      console.error("Error:", e);
      setLoading(false);
    }
  };
  fetchData();
}, []);
```

---

## 🔄 Data Flow

### Application Initialization

1. **User visits homepage** (`/`)
2. **Home component mounts** and triggers 3 parallel API calls:
   - `GET /api/home-data` → Aggregated chart
   - `GET /api/alerts` → Alert cards
   - `GET /api/skus` → SKU list
3. **Data rendered** in charts and cards

### SKU Detail Navigation

1. **User clicks alert card** or **searches SKU** or **clicks SKU button**
2. **Navigate to** `/sku/:itemId`
3. **SKUDetail component** triggers 2 API calls:
   - `GET /api/sku/:itemId` → Main chart
   - `GET /api/sku/:itemId/demand-drivers` → Side panel charts
4. **Charts rendered** with Recharts

### Alert Generation Flow

```
Backend receives /api/alerts request
    ↓
Query MongoDB for all SKUs
    ↓
For each SKU:
    - Get last 3 weeks historical (avg)
    - Get first 3 weeks forecast (avg)
    - Calculate deviation: ((forecast - historical) / historical) × 100
    ↓
Filter SKUs with |deviation| > 20%
    ↓
Sort by severity (high first) then by |deviation|
    ↓
Return top 10 alerts
```

---

## 💻 Development

### Environment Variables

**Backend (`/app/backend/.env`):**
```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="test_database"
CORS_ORIGINS="*"
```

**Frontend (`/app/frontend/.env`):**
```env
REACT_APP_BACKEND_URL=https://your-app.preview.emergentagent.com
WDS_SOCKET_PORT=443
ENABLE_HEALTH_CHECK=false
```

⚠️ **Important:** Never hardcode URLs, ports, or credentials in code. Always use environment variables.

---

### Adding New Features

#### Adding a New API Endpoint

1. **Define Pydantic model** in `backend/server.py`:
   ```python
   class NewDataModel(BaseModel):
       model_config = ConfigDict(extra="ignore")
       field_name: str
   ```

2. **Create endpoint**:
   ```python
   @api_router.get("/new-endpoint", response_model=List[NewDataModel])
   async def get_new_data():
       data = await db.collection.find({}, {"_id": 0}).to_list(100)
       return data
   ```

3. **Test with curl**:
   ```bash
   curl https://your-app/api/new-endpoint
   ```

#### Adding a New Frontend Page

1. **Create page component** in `frontend/src/pages/NewPage.js`
2. **Add route** in `frontend/src/App.js`:
   ```javascript
   <Route path="/new-page" element={<NewPage />} />
   ```
3. **Add navigation** from existing pages

---

### Hot Reload Behavior

- **Frontend:** Changes to `.js`, `.jsx`, `.css` files auto-reload
- **Backend:** Changes to `.py` files auto-reload (uvicorn --reload)
- **Environment files:** Require manual restart:
  ```bash
  sudo supervisorctl restart backend
  sudo supervisorctl restart frontend
  ```

---

### Debugging

**Backend Logs:**
```bash
# Error logs
tail -f /var/log/supervisor/backend.err.log

# Output logs
tail -f /var/log/supervisor/backend.out.log
```

**Frontend Logs:**
```bash
# Error logs
tail -f /var/log/supervisor/frontend.err.log

# Output logs
tail -f /var/log/supervisor/frontend.out.log
```

**MongoDB Queries:**
```bash
# Connect to MongoDB
mongosh mongodb://localhost:27017/test_database

# Check collections
show collections

# Query data
db.historical_data.find({"item_id": "CUST_003_ITEM_0001"})
db.forecasts.findOne({"item_id": "CUST_003_ITEM_0001"})
```

---

## 🧪 Testing

### Backend Testing

**Test file:** `/app/backend_test.py`

Run backend tests:
```bash
python /app/backend_test.py
```

Tests cover:
- API health check
- All 5 main endpoints
- Data structure validation
- Error handling (404 for invalid SKUs)

### Frontend Testing

**Manual testing checklist:**
- [ ] Home page loads with chart
- [ ] Alert cards display correctly
- [ ] Search functionality works
- [ ] SKU buttons navigate to detail page
- [ ] SKU detail page shows 52-week chart
- [ ] Demand drivers panel toggles smoothly
- [ ] Back button works
- [ ] Charts render without console errors

### Integration Testing

Use the testing agent (already configured):
```json
{
  "features_or_bugs_to_test": [
    "Home page chart",
    "Alert navigation",
    "Search functionality",
    "SKU detail charts",
    "Demand drivers panel"
  ]
}
```

---

