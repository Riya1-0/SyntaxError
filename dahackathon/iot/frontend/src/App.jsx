// import { useEffect, useState } from "react";
// // import axios from "axios";
// import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";

// function App() {
//   const [data, setSensorData] = useState([]);

//   // // Fetch history every 2s
//   // useEffect(() => {
//   //   const fetchData = async () => {
//   //     const res = await axios.get("http://127.0.0.1:8000/history");
//   //     setData(res.data);
//   //   };
//   //   fetchData();
//   //   const interval = setInterval(fetchData, 2000);
//   //   return () => clearInterval(interval);
//   // }, []);

//   useEffect(() => {
//   const fetchData = async () => {
//     const res = await fetch("http://127.0.0.1:8000/history");
//     const data = await res.json();
//     setSensorData(data);
//   };

//   fetchData();
//   const interval = setInterval(fetchData, 2000); // auto refresh every 2 sec
//   return () => clearInterval(interval);
// }, []);


//   return (
//     <div style={{ padding: "20px" }}>
//       <h1>⚡ Hydrogen IoT Dashboard</h1>

//       <h2>Temperature (°C)</h2>
//       <LineChart width={600} height={300} data={data}>
//         <CartesianGrid strokeDasharray="3 3" />
//         <XAxis dataKey="timestamp" tick={false}/>
//         <YAxis />
//         <Tooltip />
//         <Line type="monotone" dataKey="temperature" stroke="#ff7300" />
//       </LineChart>

//       <h2>Pressure (bar)</h2>
//       <LineChart width={600} height={300} data={data}>
//         <CartesianGrid strokeDasharray="3 3" />
//         <XAxis dataKey="timestamp" tick={false}/>
//         <YAxis />
//         <Tooltip />
//         <Line type="monotone" dataKey="pressure" stroke="#387908" />
//       </LineChart>

//       <h2>Storage (kg H2)</h2>
//       <LineChart width={600} height={300} data={data}>
//         <CartesianGrid strokeDasharray="3 3" />
//         <XAxis dataKey="timestamp" tick={false}/>
//         <YAxis />
//         <Tooltip />
//         <Line type="monotone" dataKey="storage" stroke="#8884d8" />
//       </LineChart>
//     </div>
//   );
// }

// export default App;





import { useEffect, useState, useRef } from "react";
import axios from "axios";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";

const API_BASE = "http://127.0.0.1:8000";
// const WS_URL = "ws://127.0.0.1:8000/ws";
const WS_URL = new WebSocket("ws://127.0.0.1:8000/ws");

const ALERT_THRESHOLD = 150.0; // keep same as backend for UX

export default function App() {
  const [data, setData] = useState([]);      // history of readings
  const [alerts, setAlerts] = useState([]);  // latest alerts
  const [Connected, setConnected] = useState(false);
  const wsRef = useRef(null);

  // connect via WebSocket for realtime updates
  useEffect(() => {
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("WS open");
      setConnected(true);
    };
    ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data);
        // snapshot contains history + alerts on connect
        if (msg.event === "snapshot") {
          setData(msg.history || []);
          setAlerts(msg.alerts || []);
        } else if (msg.event === "reading") {
          setData(prev => {
            const next = [...prev, msg.reading];
            if (next.length > 500) next.shift();
            return next;
          });
        } else if (msg.event === "alert") {
          setAlerts(prev => [msg.alert, ...prev].slice(0, 100)); // newest first
        }
      } catch (err) {
        console.error("WS parse error", err);
      }
    };
    ws.onclose = () => {
      console.log("WS closed");
      setConnected(false);
    };
    ws.onerror = (err) => {
      console.error("WS error", err);
      setConnected(false);
    };

    return () => {
      ws.close();
    };
  }, []);

  // fallback: prefetch history/alerts once (in case websocket delayed)
  useEffect(() => {
    axios.get(`${API_BASE}/history`).then(res => setData(res.data)).catch(()=>{});
    axios.get(`${API_BASE}/alerts`).then(res => setAlerts(res.data)).catch(()=>{});
  }, []);

  const latest = data.length ? data[data.length-1] : null;
  const showBanner = latest && latest.pressure > ALERT_THRESHOLD;

  return (
    <div style={{ padding: 20 }}>
      <h1>⚡ Hydrogen IoT Dashboard</h1>
      <br></br>
      {/* <div style={{ marginBottom: 12 }}>
        WebSocket: {connected ? <span style={{color:'green'}}>connected</span> : <span style={{color:'red'}}>disconnected</span>}
      </div> */}
    


      {/* ALERT BANNER */}
      {showBanner && (
        <div style={{
          backgroundColor: "crimson",
          color: "white",
          padding: "12px 16px",
          borderRadius: 6,
          marginBottom: 12,
        }}>
          ⚠️ High pressure warning — {latest.pressure} bar at {new Date(latest.timestamp).toLocaleTimeString()}
        </div>
      )}

      {/* Temperature chart */}
      <h3>Temperature (°C)</h3>
      <LineChart width={800} height={220} data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="timestamp" tick={false} />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="temperature" stroke="#ff7300" dot={false} />
      </LineChart>

      {/* Pressure chart */}
      <h3>Pressure (bar)</h3>
      <LineChart width={800} height={220} data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="timestamp" tick={false} />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="pressure" stroke="#387908" dot={false} />
      </LineChart>

      {/* Storage chart */}
      <h3>Storage (kg H2)</h3>
      <LineChart width={800} height={220} data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="timestamp" tick={false} />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="storage" stroke="#8884d8" dot={false} />
      </LineChart>

      {/* Recent alerts */}
      <h3>Recent Alerts</h3>
      <ul>
        {alerts.slice(0,10).map(a => (
          <li key={a.id}>
            <strong>{a.type}</strong> — {a.message} <em>({new Date(a.timestamp).toLocaleTimeString()})</em>
          </li>
        ))}
        {alerts.length===0 && <li>No alerts yet</li>}
      </ul>
    </div>
  );
}

