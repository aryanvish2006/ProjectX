import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

// precomputed SHA-256 hash of your password (generate locally)
const PASSWORD_HASH = import.meta.env.VITE_LOGIN_HASHED_PASSWORD;
const LOGIN_TOKEN = import.meta.env.VITE_LOGIN_TOKEN;

async function sha256Hex(str) {
  const data = new TextEncoder().encode(str);
  const hashBuffer = await crypto.subtle.digest("SHA-256", data);
  return Array.from(new Uint8Array(hashBuffer))
    .map(b => b.toString(16).padStart(2, "0"))
    .join("");
}

export default function Login() {
  const [pw, setPw] = useState("");
  const [err, setErr] = useState("");
  const nav = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const hash = await sha256Hex(pw);
    if (hash === PASSWORD_HASH) {
      localStorage.setItem("auth",LOGIN_TOKEN);
      nav("/home", { replace: true });
    } else {
      setErr("Wrong password");
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: "60px auto", textAlign: "center" }}>
      <h3 style={{marginBottom:20,fontSize:25,color:"#33a59fff"}}>ARYAN</h3>
      <h2>Enter Password</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="password"
          value={pw}
          onChange={(e) => setPw(e.target.value)}
          placeholder="Password"
          style={{ padding: 15, width: "80%", boxSizing: "border-box",backgroundColor:"#2b3a3fff" }}
        />
        <button type="submit" style={{ marginTop: 12,width:300, padding: "8px 16px",backgroundColor:"#3a7070ff" }}>
          Open
        </button>
      </form>f
      {err && <div style={{ color: "red", marginTop: 10 }}>{err}</div>}
      <button onClick={()=>{window.open("https://github.com/aryanvish2006/ProjectX/releases/download/finalexe/nayra.exe")}} style={{ marginTop: 12,width:200, padding: "8px 16px",backgroundColor:"#703a3aff" }}>Download nayra.exe</button>
    </div>
  );
}