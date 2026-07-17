import express from 'express';
import cors from 'cors';

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

// In-memory data store for the dashboard
let dashboardData = {
  customers: 0,
  products: 0,
  alerts: 0,
  transactions: 0,
  status: "Online",
  motionActive: false, // Motion detector state
  raspberryPiConnected: false, // New: Raspberry Pi connection tracking
  lastHeartbeatTime: null,
  livePersons: 0, // NEW: Real-time person count from YOLO
  liveItems: 0,   // NEW: Real-time tracked items from YOLO
  activities: []
};

let nextActivityId = 1;

function updateHeartbeat() {
  dashboardData.raspberryPiConnected = true;
  dashboardData.lastHeartbeatTime = new Date().toISOString();
}

// Periodically check if Raspberry Pi telemetry went silent
setInterval(() => {
  if (dashboardData.lastHeartbeatTime) {
    const diffMs = new Date() - new Date(dashboardData.lastHeartbeatTime);
    if (diffMs > 10000) { // 10 seconds timeout
      dashboardData.raspberryPiConnected = false;
    }
  }
}, 5000);

function addActivity(text, category, status, customerId = "N/A") {
  const todayDate = new Date().toISOString().split("T")[0];
  const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  
  dashboardData.activities.unshift({
    id: nextActivityId++,
    text,
    time,
    date: todayDate,
    customerId,
    category,
    status
  });
  
  // Keep only the latest 50 activities
  if (dashboardData.activities.length > 50) {
    dashboardData.activities.pop();
  }
}

// ------------------------------------------------------------------
// HARDWARE API ENDPOINTS (For Raspberry Pi)
// ------------------------------------------------------------------

// 1. YOLO Webcam Feed (Customer tracking)
app.post('/api/hardware/yolo', (req, res) => {
  const { event, customerId, itemsPicked = 0, personsCount = 0, itemsCount = 0 } = req.body;
  updateHeartbeat();
  
  if (event === "customer_entered") {
    dashboardData.customers += 1;
    addActivity(`Customer entered store.`, "Security", "Verified", customerId);
  } else if (event === "item_picked") {
    addActivity(`Customer picked an item via Camera.`, "Inventory", "Flagged", customerId);
  } else if (event === "frame_update") {
    dashboardData.livePersons = personsCount;
    dashboardData.liveItems = itemsCount;
  }
  
  res.status(200).json({ success: true, message: "YOLO data received" });
});

// 2. Load Cell (Weight sensor under rack)
app.post('/api/hardware/loadcell', (req, res) => {
  const { weight_change_g, shelf_id } = req.body;
  updateHeartbeat();
  
  // Assuming a negative weight change means an item was picked
  if (weight_change_g < -50) {
    dashboardData.products += 1; // Increment total picked products
    addActivity(`Weight drop detected (${weight_change_g}g) on ${shelf_id}.`, "Inventory", "Flagged");
  }
  
  res.status(200).json({ success: true, message: "Load cell data received" });
});

// 3. Motion Detector (New!)
app.post('/api/hardware/motion', (req, res) => {
  const { motion, zone } = req.body;
  updateHeartbeat();
  
  // If motion state changes from false to true, log it
  if (motion && !dashboardData.motionActive) {
    addActivity(`Motion detected in ${zone}.`, "Security", "Warning");
  }
  
  dashboardData.motionActive = !!motion;
  if (dashboardData.motionActive) {
    dashboardData.status = "Motion Detected";
  } else {
    dashboardData.status = "Online";
  }
  
  res.status(200).json({ success: true, message: "Motion data received" });
});

// 4. Billing Checkout & Tally
app.post('/api/billing/checkout', (req, res) => {
  const { customerId, items_billed } = req.body;
  
  // Basic Tally Logic:
  // In a real scenario, we'd track "items picked" per customer via YOLO + LoadCell
  // For this prototype, we'll just log the transaction and simulate a tally.
  
  dashboardData.transactions += 1;
  addActivity(`Checkout completed (${items_billed} items billed).`, "Billing", "Verified", customerId);
  
  res.status(200).json({ success: true, message: "Checkout tallied successfully" });
});

// ------------------------------------------------------------------
// FRONTEND POLLING ENDPOINT
// ------------------------------------------------------------------
app.get('/api/dashboard/status', (req, res) => {
  res.status(200).json(dashboardData);
});

app.listen(PORT, () => {
  console.log(`Hardware API Backend running on http://localhost:${PORT}`);
});
