import { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { MagnifyingGlass, TrendUp, TrendDown, Warning } from "@phosphor-icons/react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Home = () => {
  const [chartData, setChartData] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [skus, setSkus] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchHomeData();
    fetchAlerts();
    fetchSkus();
  }, []);

  const fetchHomeData = async () => {
    try {
      const response = await axios.get(`${API}/home-data`);
      setChartData(response.data.chart_data);
    } catch (e) {
      console.error("Error fetching home data:", e);
    }
  };

  const fetchAlerts = async () => {
    try {
      const response = await axios.get(`${API}/alerts`);
      setAlerts(response.data);
    } catch (e) {
      console.error("Error fetching alerts:", e);
    }
  };

  const fetchSkus = async () => {
    try {
      const response = await axios.get(`${API}/skus`);
      setSkus(response.data);
      setLoading(false);
    } catch (e) {
      console.error("Error fetching SKUs:", e);
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/sku/${searchQuery.trim()}`);
    }
  };

  const handleAlertClick = (itemId) => {
    navigate(`/sku/${itemId}`);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const getSeverityColor = (severity) => {
    return severity === 'high' ? '#E11D48' : '#FACC15';
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg" style={{ fontFamily: 'IBM Plex Sans' }}>Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen" style={{ background: '#FFFFFF' }}>
      {/* Header */}
      <header
        className="border-b sticky top-0 z-50"
        style={{
          background: '#FFFFFF',
          borderBottom: '1px solid #E4E4E7',
        }}
      >
        <div className="px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <img 
                src="https://customer-assets.emergentagent.com/job_build-dash-26/artifacts/29or6fl6_image.png" 
                alt="Demand Planning Logo"
                className="h-8"
                style={{ objectFit: 'contain' }}
              />
            </div>

            {/* Search Bar */}
            <form onSubmit={handleSearch} className="flex-1 max-w-md mx-8">
              <div className="relative">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search SKU (e.g., CUST_003_ITEM_0001)"
                  data-testid="sku-search-input"
                  className="w-full px-4 py-2 pr-10 border focus:outline-none focus:ring-2 focus:ring-black"
                  style={{
                    fontFamily: 'IBM Plex Sans',
                    border: '1px solid #E4E4E7',
                    borderRadius: '2px',
                  }}
                />
                <button
                  type="submit"
                  data-testid="sku-search-button"
                  className="absolute right-2 top-1/2 -translate-y-1/2"
                >
                  <MagnifyingGlass size={20} color="#71717A" weight="bold" />
                </button>
              </div>
            </form>

            <div
              className="w-10 h-10 rounded-full"
              style={{
                background: '#F4F4F5',
                border: '1px solid #E4E4E7',
              }}
            />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="px-6 lg:px-8 py-8">
        {/* Page Title */}
        <div className="mb-8">
          <h2
            className="text-3xl font-bold tracking-tight mb-2"
            style={{ fontFamily: 'Chivo', color: '#09090B' }}
          >
            Overview Dashboard
          </h2>
          <p
            className="text-base"
            style={{ fontFamily: 'IBM Plex Sans', color: '#71717A' }}
          >
            Monitor weekly sales performance and AI-generated forecasts
          </p>
        </div>

        {/* Aggregated Chart */}
        <div
          className="mb-6 p-6 border"
          data-testid="aggregated-chart-container"
          style={{
            border: '1px solid #E4E4E7',
            borderRadius: '2px',
            background: '#FFFFFF',
          }}
        >
          <h3
            className="text-xl font-bold tracking-tight mb-4"
            style={{ fontFamily: 'Chivo', color: '#09090B' }}
          >
            Sales Performance: Last 13 Weeks + 39 Week Forecast
          </h3>
          <div style={{ width: '100%', height: '400px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#F4F4F5" />
                <XAxis
                  dataKey="timestamp"
                  tickFormatter={formatDate}
                  style={{ fontFamily: 'IBM Plex Sans', fontSize: '12px' }}
                />
                <YAxis style={{ fontFamily: 'IBM Plex Sans', fontSize: '12px' }} />
                <Tooltip
                  contentStyle={{
                    fontFamily: 'IBM Plex Sans',
                    border: '1px solid #E4E4E7',
                    borderRadius: '2px',
                  }}
                />
                <Legend
                  wrapperStyle={{ fontFamily: 'IBM Plex Sans', fontSize: '14px' }}
                />
                <Line
                  type="monotone"
                  dataKey="units_sold"
                  stroke="#2563EB"
                  strokeWidth={2}
                  dot={false}
                  name="Units Sold"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Alerts Section */}
        <div className="mb-8">
          <h3
            className="text-2xl font-bold tracking-tight mb-4"
            style={{ fontFamily: 'Chivo', color: '#09090B' }}
          >
            Forecast Alerts
          </h3>
          <p
            className="text-sm mb-4"
            style={{ fontFamily: 'IBM Plex Sans', color: '#71717A' }}
          >
            Items requiring attention based on forecast accuracy
          </p>

          {alerts.length === 0 ? (
            <div
              className="p-6 border text-center"
              style={{
                border: '1px solid #E4E4E7',
                borderRadius: '2px',
                background: '#F4F4F5',
              }}
            >
              <p style={{ fontFamily: 'IBM Plex Sans', color: '#71717A' }}>
                No alerts at this time. All forecasts are within normal ranges.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {alerts.map((alert) => (
                <div
                  key={alert.item_id}
                  onClick={() => handleAlertClick(alert.item_id)}
                  data-testid={`alert-card-${alert.item_id}`}
                  className="alert-card p-4 border cursor-pointer"
                  style={{
                    border: `2px solid ${getSeverityColor(alert.severity)}`,
                    borderRadius: '2px',
                    background: '#FFFFFF',
                  }}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      {alert.deviation_percent > 0 ? (
                        <TrendUp
                          size={20}
                          color={getSeverityColor(alert.severity)}
                          weight="bold"
                        />
                      ) : (
                        <TrendDown
                          size={20}
                          color={getSeverityColor(alert.severity)}
                          weight="bold"
                        />
                      )}
                      <span
                        className="text-xs font-bold uppercase tracking-wider"
                        style={{
                          fontFamily: 'IBM Plex Sans',
                          color: getSeverityColor(alert.severity),
                        }}
                      >
                        {alert.severity} PRIORITY
                      </span>
                    </div>
                  </div>
                  <h4
                    className="text-lg font-bold mb-2"
                    style={{ fontFamily: 'Chivo', color: '#09090B' }}
                  >
                    {alert.item_id}
                  </h4>
                  <p
                    className="text-sm"
                    style={{ fontFamily: 'IBM Plex Sans', color: '#71717A' }}
                  >
                    {alert.message}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Quick SKU Access */}
        <div>
          <h3
            className="text-2xl font-bold tracking-tight mb-4"
            style={{ fontFamily: 'Chivo', color: '#09090B' }}
          >
            All SKUs
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-3">
            {skus.slice(0, 10).map((sku) => (
              <button
                key={sku.item_id}
                onClick={() => navigate(`/sku/${sku.item_id}`)}
                data-testid={`sku-button-${sku.item_id}`}
                className="p-3 border text-left hover:bg-zinc-100 transition-colors"
                style={{
                  border: '1px solid #E4E4E7',
                  borderRadius: '2px',
                  fontFamily: 'IBM Plex Sans',
                  fontSize: '14px',
                  color: '#09090B',
                }}
              >
                {sku.item_id}
              </button>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
};

export default Home;
