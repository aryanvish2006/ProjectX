const express = require("express")
const WebSocket = require("ws")
const multer = require("multer")
const path = require("path")
const fs = require("fs")

const app = express();
const upload = multer({dest:"uploads/"});
 
const clients = [];
const server = app.listen(3000,()=>{
    console.log("server running at 3000")
})
const wss = new WebSocket.Server({noServer:true});
let client = null;

wss.on("connection",ws=>{
    let clientInfo = {ws,deviceName:null};
    clients.push(clientInfo)
    console.log("Client connected");

    ws.on("message",value=>{
        const msg = value.toString();
        if(msg.startsWith("Connected")){
            clientInfo.deviceName = msg.split(":")[1];
            console.log("client device name : ",clientInfo.deviceName);
        }else{
            console.log(`Message from ${clientInfo.deviceName || "unknown" }`,msg)
        }
    })
    ws.on("close",()=>{
        console.log(`Client ${clientInfo.deviceName || "unknown"} disconneted`);
        clients.splice(clients.indexOf(clientInfo),1);

        console.log("list : ",clients)
    })
});

server.on("upgrade",(request,socket,head)=>{
    wss.handleUpgrade(request,socket,head,ws=>{
        wss.emit("connection",ws,request)
    })
})

app.post("/upload",upload.single("screenshot"),(req,res)=>{
    const savePath = path.join("uploads",req.file.originalname);
    fs.renameSync(req.file.path,savePath);
    console.log("saved screenshot",req.file.originalname);
    res.send("Saved");
})
app.get("/clients",(req,res)=>{
    const connectedClients = clients.map((c,index)=>({
        id:index,
        deviceName:c.deviceName||"unknown"
    }))
    res.json(connectedClients)
})

app.get("/send", (req, res) => {
    const index = parseInt(req.query.index); 
    const msg = req.query.msg;

    if (isNaN(index) || !msg) return res.send("Usage: /send?index=0&msg=yourMessage");

    const target = clients[index];
    if (!target) return res.send(`Client at index ${index} not found`);

    if (target.ws.readyState === WebSocket.OPEN) {
        target.ws.send(msg);
        res.send(`Message sent to client[${index}]: ${msg}`);
    } else {
        res.send(`Client[${index}] is disconnected`);
    }
});

app.get("/broadcast", (req, res) => {
    const msg = req.query.msg;
    if (!msg) return res.send("Usage: /broadcast?msg=yourMessage");

    clients.forEach(c => {
        if (c.ws.readyState === WebSocket.OPEN) c.ws.send(msg);
    });
    res.send("Message broadcasted to all clients");
});
