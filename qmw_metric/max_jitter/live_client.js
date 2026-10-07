// Max node.script WebSocket client. Requests the documented JSON fallback.
const maxApi = require("max-api");
const fs = require("fs");
let socket = null, timer = null, stopped = true, backoff = 250;
let url = "ws://127.0.0.1:8767/qmw/metric/v1?format=json";
function status(value){ maxApi.outlet("status", value); }
function connect(){
  stopped=false; status("connecting"); socket=new WebSocket(url);
  socket.onopen=()=>{backoff=250;status("live")};
  socket.onmessage=e=>{if(typeof e.data!=="string")return;const p=JSON.parse(e.data);if(p.type!=="hello")maxApi.outlet("frame",e.data)};
  socket.onerror=()=>socket.close();
  socket.onclose=()=>{if(stopped)return;status("reconnecting");timer=setTimeout(connect,backoff);backoff=Math.min(5000,backoff*2)};
}
maxApi.addHandler("connect", value=>{if(value)connect();else{stopped=true;clearTimeout(timer);socket?.close();status("offline")}});
maxApi.addHandler("url", value=>{url=String(value)});
maxApi.addHandler("fixture", (path, interval=900)=>{
  const fixture=JSON.parse(fs.readFileSync(String(path),"utf8"));
  if(fixture.fixture_contract!=="qmw_metric.controlled_scenes.transport_fixture.v1"){
    status("rejected fixture contract");return;
  }
  let index=0;status("fixture");
  const next=()=>{if(index>=fixture.frames.length){status("fixture complete");return}maxApi.outlet("frame",JSON.stringify(fixture.frames[index++]));timer=setTimeout(next,Math.max(50,Number(interval)))};
  next();
});
