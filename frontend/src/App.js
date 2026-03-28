import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "@/pages/Home";
import SKUDetail from "@/pages/SKUDetail";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/sku/:itemId" element={<SKUDetail />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
