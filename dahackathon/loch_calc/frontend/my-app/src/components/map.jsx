

import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { useState } from "react";
import axios from "axios";
import L from "leaflet";
import iconUrl from "leaflet/dist/images/marker-icon.png";
import iconShadow from "leaflet/dist/images/marker-shadow.png";

let DefaultIcon = L.icon({ iconUrl, shadowUrl: iconShadow });
L.Marker.prototype.options.icon = DefaultIcon;

function LocationMarker() {
  const [position, setPosition] = useState(null);
  const [lcoh, setLcoh] = useState(null);

  useMapEvents({
    click: async (e) => {
      const { lat, lng } = e.latlng;
      setPosition([lat, lng]);

      try {
        const res = await axios.get("http://localhost:8000/lcoh", {
          params: { lat, lon: lng },
        });
        setLcoh(res.data.lcoh);
      } catch (error) {
        console.error("API error:", error);
      }
    },
  });

  return position === null ? null : (
    <Marker position={position}>
      <Popup>
        📍 Lat: {position[0].toFixed(2)}, Lon: {position[1].toFixed(2)} <br />
        💰 LCOH: {lcoh ? `${lcoh} $/kg` : "Calculating..."}
      </Popup>
    </Marker>
  );
}

export default function Map() {
  return (
    <MapContainer center={[20.5937, 78.9629]} zoom={5} style={{ height: "500px", width: "100%" }}>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <LocationMarker />
    </MapContainer>
  );
}

