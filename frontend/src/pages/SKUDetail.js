import { useEffect, useState } from "react";
import axios from "axios";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, ChartLine, X } from "@phosphor-icons/react";
import { motion, AnimatePresence } from "framer-motion";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  ComposedChart,
} from "recharts";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SKUDetail = () => {
  const { itemId } = useParams();
  const navigate = useNavigate();
  const [chartData, setChartData] = useState([]);
  const [demandDrivers, setDemandDrivers] = useState([]);
  const [showDriversPanel, setShowDriversPanel] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchSKUDetail();
    fetchDemandDrivers();
  }, [itemId]);

  const fetchSKUDetail = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`${API}/sku/${itemId}`);
      setChartData(response.data.chart_data);
      setLoading(false);
    } catch (e) {
      console.error("Error fetching SKU detail:", e);
      setError("SKU not found or error loading data");
      setLoading(false);
    }
  };

  const fetchDemandDrivers = async () => {
    try {
      const response = await axios.get(`${API}/sku/${itemId}/demand-drivers`);
      setDemandDrivers(response.data.demand_drivers);
    } catch (e) {
      console.error("Error fetching demand drivers:", e);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg" style={{ fontFamily: 'IBM Plex Sans' }}>Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center">
        <div className="text-lg mb-4" style={{ fontFamily: 'IBM Plex Sans', color: '#E11D48' }}>
          {error}
        </div>
        <button
          onClick={() => navigate('/')}
          className="px-4 py-2 border"
          style={{
            fontFamily: 'IBM Plex Sans',
            border: '1px solid #09090B',
            background: '#09090B',
            color: '#FFFFFF',
          }}
        >
          Back to Home
        </button>
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
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/')}
                data-testid="back-to-home-button"
                className="p-2 hover:bg-zinc-100 transition-colors"
                style={{ borderRadius: '2px' }}
              >
                <ArrowLeft size={24} color="#09090B" weight="bold" />
              </button>
              <img 
                src="https://customer-assets.emergentagent.com/job_build-dash-26/artifacts/29or6fl6_image.png" 
                alt="Demand Planning Logo"
                className="h-10"
                style={{ objectFit: 'contain' }}
              />
              <span
                className="text-lg font-bold tracking-tight"
                style={{ fontFamily: 'Chivo', color: '#09090B' }}
              >
                Workbench
              </span>
            </div>

            <button
              onClick={() => setShowDriversPanel(!showDriversPanel)}
              data-testid="toggle-drivers-panel-button"
              className="flex items-center gap-2 px-4 py-2 border hover:bg-zinc-100 transition-colors"
              style={{
                fontFamily: 'IBM Plex Sans',
                border: '1px solid #E4E4E7',
                borderRadius: '2px',
                background: showDriversPanel ? '#09090B' : '#FFFFFF',
                color: showDriversPanel ? '#FFFFFF' : '#09090B',
              }}
            >
              <ChartLine size={20} weight="bold" />
              Demand Drivers
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex">
        <main className="flex-1 px-6 lg:px-8 py-8">
          {/* SKU Info */}
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-2">
              <span
                className="text-xs font-bold uppercase tracking-wider px-2 py-1"
                style={{
                  fontFamily: 'IBM Plex Sans',
                  background: '#F4F4F5',
                  color: '#71717A',
                  borderRadius: '2px',
                }}
              >
                SKU DETAIL
              </span>
            </div>
            <h2
              className="text-4xl font-black tracking-tight mb-2"
              style={{ fontFamily: 'Chivo', color: '#09090B' }}
              data-testid="sku-detail-title"
            >
              {itemId}
            </h2>
            <p
              className="text-base"
              style={{ fontFamily: 'IBM Plex Sans', color: '#71717A' }}
            >
              52-week view: 13 weeks historical + 39 weeks forecast
            </p>
          </div>

          {/* Main Chart */}
          <div
            className="border p-6"
            data-testid="sku-forecast-chart"
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
              Forecast & Historical Performance
            </h3>
            <div style={{ width: '100%', height: '500px' }}>
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
                    strokeWidth={3}
                    dot={false}
                    name="Units Sold"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </main>

        {/* Demand Drivers Side Panel */}
        <AnimatePresence>
          {showDriversPanel && (
            <motion.aside
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'tween', duration: 0.3 }}
              className="w-96 border-l"
              data-testid="demand-drivers-panel"
              style={{
                borderLeft: '1px solid #E4E4E7',
                background: '#FFFFFF',
                position: 'fixed',
                right: 0,
                top: 0,
                height: '100vh',
                overflowY: 'auto',
              }}
            >
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3
                    className="text-xl font-bold tracking-tight"
                    style={{ fontFamily: 'Chivo', color: '#09090B' }}
                  >
                    Demand Drivers
                  </h3>
                  <button
                    onClick={() => setShowDriversPanel(false)}
                    data-testid="close-drivers-panel-button"
                    className="p-1 hover:bg-zinc-100 transition-colors"
                    style={{ borderRadius: '2px' }}
                  >
                    <X size={20} color="#09090B" weight="bold" />
                  </button>
                </div>

                {/* Average Unit Price Chart */}
                <div className="mb-6">
                  <h4
                    className="text-base font-bold mb-3"
                    style={{ fontFamily: 'Chivo', color: '#09090B' }}
                  >
                    Average Unit Price
                  </h4>
                  <div style={{ width: '100%', height: '200px' }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={demandDrivers}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#F4F4F5" />
                        <XAxis
                          dataKey="timestamp"
                          tickFormatter={formatDate}
                          style={{ fontFamily: 'IBM Plex Sans', fontSize: '10px' }}
                        />
                        <YAxis style={{ fontFamily: 'IBM Plex Sans', fontSize: '10px' }} />
                        <Tooltip
                          contentStyle={{
                            fontFamily: 'IBM Plex Sans',
                            fontSize: '12px',
                            border: '1px solid #E4E4E7',
                          }}
                        />
                        <Line
                          type="monotone"
                          dataKey="avg_unit_price"
                          stroke="#10B981"
                          strokeWidth={2}
                          dot={false}
                          name="Avg Price"
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Customer In-Stock Chart */}
                <div>
                  <h4
                    className="text-base font-bold mb-3"
                    style={{ fontFamily: 'Chivo', color: '#09090B' }}
                  >
                    Customer In-Stock Rate
                  </h4>
                  <div style={{ width: '100%', height: '200px' }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={demandDrivers}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#F4F4F5" />
                        <XAxis
                          dataKey="timestamp"
                          tickFormatter={formatDate}
                          style={{ fontFamily: 'IBM Plex Sans', fontSize: '10px' }}
                        />
                        <YAxis
                          domain={[0, 1]}
                          style={{ fontFamily: 'IBM Plex Sans', fontSize: '10px' }}
                        />
                        <Tooltip
                          contentStyle={{
                            fontFamily: 'IBM Plex Sans',
                            fontSize: '12px',
                            border: '1px solid #E4E4E7',
                          }}
                        />
                        <Line
                          type="monotone"
                          dataKey="cust_instock"
                          stroke="#E11D48"
                          strokeWidth={2}
                          dot={false}
                          name="In-Stock"
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Legend */}
                <div className="mt-6 p-3" style={{ background: '#F4F4F5', borderRadius: '2px' }}>
                  <p
                    className="text-xs font-bold uppercase tracking-wider mb-2"
                    style={{ fontFamily: 'IBM Plex Sans', color: '#71717A' }}
                  >
                    About Demand Drivers
                  </p>
                  <p className="text-sm" style={{ fontFamily: 'IBM Plex Sans', color: '#09090B' }}>
                    These metrics show both historical actuals and projected future values that
                    influence demand forecasting.
                  </p>
                </div>
              </div>
            </motion.aside>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default SKUDetail;
