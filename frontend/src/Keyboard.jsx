import React, { useState } from "react";

const KEY_LAYOUT = [
  ["Esc","F1","F2","F3","F4","F5","F6","F7","F8","F9","F10","F11","F12"],
  ["`","1","2","3","4","5","6","7","8","9","0","-","=","Backspace"],
  ["Tab","q","w","e","r","t","y","u","i","o","p","[","]","\\"],
  ["CapsLock","a","s","d","f","g","h","j","k","l",";","'","Enter"],
  ["Shift","z","x","c","v","b","n","m",",",".","/","Shift"],
  ["Ctrl","Win","Alt","Space","Alt","Win","Menu","Ctrl","left","down","up","right"]
];

const SPECIAL_KEYS = ["Backspace","Tab","Enter","Shift","CapsLock","Ctrl","Alt","Win","Menu","Space","left","down","up","right"];

export default function Keyboard({ sendCommand }) {
  const [shift, setShift] = useState(false);
  const [caps, setCaps] = useState(false);

  const handleKey = (key) => {
    if(key === "Shift") { setShift(!shift); return; }
    if(key === "CapsLock") { setCaps(!caps); return; }

    let outputKey = key;

    if(key.length === 1 && key.match(/[a-z]/i)){
      if((shift && !caps) || (!shift && caps) || (shift && caps)) outputKey = key.toUpperCase();
      else outputKey = key.toLowerCase();
    }

    if(key === "Space") outputKey = " ";

    if(shift && key !== "Shift") setShift(false);

    sendCommand(`press ${outputKey}`, false);
  }

  const renderKey = (key) => (
    <button
      key={key + Math.random()}
      onClick={() => handleKey(key)}
      style={{
        padding: "10px 14px",
        minWidth: key === "Space" ? 200 : SPECIAL_KEYS.includes(key) ? 60 : 40,
        borderRadius: 6,
        border: "1px solid #333",
        background: "#222",
        color: "#fff",
        cursor: "pointer",
        fontWeight: "bold",
        boxShadow: "0 2px 4px rgba(0,0,0,0.5)",
        flex: key === "Space" ? "3 1 200px" : SPECIAL_KEYS.includes(key) ? "1 1 60px" : "1 1 40px",
        textAlign: "center",
        userSelect: "none"
      }}
    >
      {key === "Space" ? "␣" : key}
    </button>
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 5, width: "100%" }}>
      {KEY_LAYOUT.map((row, i) => (
        <div key={i} style={{ display: "flex", gap: 5, flexWrap: "wrap", justifyContent: "center" }}>
          {row.map(renderKey)}
        </div>
      ))}
    </div>
  )
}
