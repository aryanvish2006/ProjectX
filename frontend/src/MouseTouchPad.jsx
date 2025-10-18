import React, { useState, useRef } from "react";

export default function MouseTouchpad({ sendCommand }) {
  const padRef = useRef(null);
  const [ballPos, setBallPos] = useState({ x: 50, y: 50 }); 
  const dragging = useRef(false);
  const offset = useRef({ x: 0, y: 0 });

  // Default virtual screen size
  const [virtualWidth, setVirtualWidth] = useState(1366);
  const [virtualHeight, setVirtualHeight] = useState(768);

  // Drag start
  const handlePointerDown = (e) => {
    const pad = padRef.current.getBoundingClientRect();
    const ballX = (ballPos.x / 100) * pad.width;
    const ballY = (ballPos.y / 100) * pad.height;

    const mouseX = e.clientX - pad.left;
    const mouseY = e.clientY - pad.top;

    offset.current = { x: mouseX - ballX, y: mouseY - ballY };
    dragging.current = true;
  };

  // Drag move
  const handlePointerMove = (e) => {
    if (!dragging.current) return;

    const pad = padRef.current.getBoundingClientRect();
    const mouseX = e.clientX - pad.left;
    const mouseY = e.clientY - pad.top;

    let newX = ((mouseX - offset.current.x) / pad.width) * 100;
    let newY = ((mouseY - offset.current.y) / pad.height) * 100;

    newX = Math.max(0, Math.min(100, newX));
    newY = Math.max(0, Math.min(100, newY));

    setBallPos({ x: newX, y: newY });
  };

  // Drag end — send command
  const handlePointerUp = () => {
    if (!dragging.current) return;
    dragging.current = false;

    const absX = Math.round((ballPos.x / 100) * virtualWidth);
    const absY = Math.round((ballPos.y / 100) * virtualHeight);

    sendCommand(`moveto ${absX} ${absY}`);
  };

  // Handle virtual screen size change
  const handleWidthChange = (e) => setVirtualWidth(Number(e.target.value));
  const handleHeightChange = (e) => setVirtualHeight(Number(e.target.value));

  // Request screen size from Python client
  const requestScreenSize = () => sendCommand("getscreensize");

  return (
    <div style={{ marginTop: 20, display: "flex", flexDirection: "column", alignItems: "center" }}>
      
      {/* Virtual Screen Input */}
      <div style={{ display: "flex", gap: 10, marginBottom: 15 }}>
        <input
          type="number"
          value={virtualWidth}
          onChange={handleWidthChange}
          placeholder="Width"
          style={inputStyle}
        />
        <input
          type="number"
          value={virtualHeight}
          onChange={handleHeightChange}
          placeholder="Height"
          style={inputStyle}
        />
        <button onClick={requestScreenSize} style={btnStyle}>Get Screen Size</button>
      </div>

      {/* Touchpad */}
      <div
        ref={padRef}
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerLeave={handlePointerUp}
        style={{
          width: "min(90vw, 400px)",
          aspectRatio: "16 / 9",
          background: "#222",
          borderRadius: 12,
          position: "relative",
          touchAction: "none",
          userSelect: "none",
        }}
      >
        <div
          style={{
            width: 35,
            height: 35,
            borderRadius: "50%",
            background: "red",
            position: "absolute",
            left: `${ballPos.x}%`,
            top: `${ballPos.y}%`,
            transform: "translate(-50%, -50%)",
            cursor: "grab",
          }}
        ></div>
      </div>

      {/* Mouse buttons */}
      <div style={{ display: "flex", gap: 10, marginTop: 15, flexWrap: "wrap" }}>
        <button style={mouseBtnStyle} onClick={() => sendCommand("mouseleft")}>Left Click</button>
        <button style={mouseBtnStyle} onClick={() => sendCommand("mouseright")}>Right Click</button>
      </div>
    </div>
  );
}

// Styles
const inputStyle = {
  padding: "8px",
  borderRadius: 6,
  border: "1px solid #333",
  width: 80,
};

const btnStyle = {
  padding: "4px 6px",
  borderRadius: 6,
  border: "1px solid #333",
  background: "#555",
  color: "#fff",
  cursor: "pointer",
};

const mouseBtnStyle = {
  padding: "12px 20px",
  borderRadius: 6,
  border: "1px solid #333",
  background: "#555",
  color: "#fff",
  cursor: "pointer",
  fontWeight: "bold",
  boxShadow: "0 2px 4px rgba(0,0,0,0.5)",
  minWidth: 100
};
