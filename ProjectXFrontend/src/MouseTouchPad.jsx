import React, { useState, useRef } from "react";

export default function MouseTouchpad({ sendCommand }) {
  const [liveMouse, setLiveMouse] = useState(false); // toggle mode
  const [ballPos, setBallPos] = useState({ x: 0, y: 0 }); // relative to center
  const startPos = useRef({ x: 0, y: 0 }); // starting drag coordinates
  const dragging = useRef(false);

  const toggleLive = () => setLiveMouse(prev => !prev);

  const handlePointerDown = (e) => {
    dragging.current = true;
    startPos.current = { x: e.clientX, y: e.clientY };
    setBallPos({ x: 0, y: 0 }); // reset ball for this drag
  };

  const handlePointerMove = (e) => {
    if (!dragging.current) return; // only move if dragging

    if (liveMouse) {
      // Live mode: send continuous movements
      const dx = e.movementX;
      const dy = e.movementY;
      sendCommand(`mousemove ${dx} ${dy}`, false);
    } else {
      // Batch mode: update ball position relative to drag start
      const dx = e.clientX - startPos.current.x;
      const dy = e.clientY - startPos.current.y;
      setBallPos({ x: dx, y: dy });
    }
  };

  const handlePointerUp = () => {
    if (!dragging.current) return;

    if (!liveMouse) {
      // Batch mode: send total delta once
      sendCommand(`mousemove ${ballPos.x} ${ballPos.y}`, false);
      setBallPos({ x: 0, y: 0 }); // reset ball
    }

    dragging.current = false;
  };

  return (
    <div style={{ marginTop: 20 }}>
      <button onClick={toggleLive} style={{ marginBottom: 10, padding: "8px 16px" }}>
        {liveMouse ? "Live Mouse ON" : "Batch Mode (Drag & Release)"}
      </button>

      <div
        style={{
          width: "100%",
          height: 250,
          background: "#333",
          borderRadius: 10,
          position: "relative",
          touchAction: "none",
          userSelect: "none",
          overflow: "hidden"
        }}
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerLeave={handlePointerUp} // release if pointer leaves area
      >
        {/* Ball indicator only shows while dragging in batch mode */}
        {!liveMouse && dragging.current && (
          <div
            style={{
              width: 30,
              height: 30,
              borderRadius: "50%",
              background: "red",
              position: "absolute",
              top: "50%",
              left: "50%",
              transform: `translate(calc(${ballPos.x}px - 50%), calc(${ballPos.y}px - 50%))`,
            }}
          ></div>
        )}
      </div>

      {/* Mouse buttons */}
      <div style={{ display: "flex", justifyContent: "center", gap: 10, marginTop: 10, flexWrap: "wrap" }}>
        <button style={mouseBtnStyle} onClick={() => sendCommand("mouseleft", false)}>Left Click</button>
        <button style={mouseBtnStyle} onClick={() => sendCommand("mouseright", false)}>Right Click</button>
      </div>
    </div>
  );
}

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
