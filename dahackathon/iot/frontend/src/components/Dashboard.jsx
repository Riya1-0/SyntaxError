// import React, { useEffect, useState } from "react";

// function Dashboard() {
//   const [socketStatus, setSocketStatus] = useState("disconnected");
//   const [Data, setData] = useState([]);
//   const [alerts, setAlerts] = useState([]);

//   useEffect(() => {
//     const ws = new WebSocket("ws://127.0.0.1:8000/ws");

//     ws.onopen = () => setSocketStatus("connected");
//     ws.onclose = () => setSocketStatus("disconnected");
//     ws.onerror = () => setSocketStatus("error");

//     ws.onmessage = (event) => {
//       const msg = JSON.parse(event.data);
//       setData((prev) => [...prev.slice(-19), msg]); // keep last 20 points

//       // Alert rule: pressure > 150 bar
//       if (msg.pressure > 150) {
//         setAlerts((prev) => [
//           { text: `⚠️ High Pressure Alert: ${msg.pressure} bar`, time: msg.timestamp },
//           ...prev.slice(0, 4),
//         ]);
//       }
//     };

//     return () => ws.close();
//   }, []);

//   return (
//     <div>
//       <h2>⚡ Hydrogen IoT Dashboard</h2>
//       <p>WebSocket: <span style={{ color: socketStatus === "connected" ? "green" : "red" }}>{socketStatus}</span></p>

//       <div>
//         {alerts.map((a, idx) => (
//           <div key={idx} style={{ background: "red", color: "white", padding: "5px", margin: "5px 0" }}>
//             {a.text} ({a.time})
//           </div>
//         ))}
//       </div>

//       {/* TODO: Add your charts using data */}
//     </div>
//   );
// }

// export default Dashboard;



import { useEffect, useState } from "react";
import AlertBanner from "./AlertBanner";

function Dashboard() {
  const [data, setData] = useState({});

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/iot");
    ws.onmessage = (event) => {
      setData(JSON.parse(event.data));
    };
    return () => ws.close();
  }, []);

  return (
    <div className="p-4 space-y-4">
      <h1 className="text-2xl font-bold">Hydrogen IoT Dashboard</h1>

      <AlertBanner alert={data.alert} />

      <div className="grid grid-cols-3 gap-4">
        <div className="p-4 shadow rounded bg-gray-100">
          <p>🌡️ Temperature</p>
          <h2 className="text-xl">{data.temperature} °C</h2>
        </div>
        <div className="p-4 shadow rounded bg-gray-100">
          <p>⛽ Pressure</p>
          <h2 className="text-xl">{data.pressure} bar</h2>
        </div>
        <div className="p-4 shadow rounded bg-gray-100">
          <p>📦 Storage</p>
          <h2 className="text-xl">{data.storage} %</h2>
        </div>
      </div>
    </div>
  );
}
export default Dashboard;
