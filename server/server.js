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
let client = null;

wss.on("connection",ws=>{
    client=ws;
    console.log("Client connected");
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

app.get("/send",(req,res)=>{
    const message = req.query.msg;
    if(client){
        client.send(message);
        res.send("message sent");
    }else{
        res.send("No client connected");
    }
})

