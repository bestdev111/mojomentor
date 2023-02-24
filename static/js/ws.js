console.log("Websocket file loaded successfully");
const loc = window.location;
const wsProtocol = (loc.protocol == "https:") ? 'wss' : 'ws';
const wsUrl = `${wsProtocol}://${loc.host}/ws/chat`;

// websockets codes
const ws = new WebSocket(wsUrl);
ws.onopen = (event) => {
  console.log("WebSocket connected...");
  console.log(event);
};
var val = 0;
ws.onmessage = (event) => {
  val++
  let temp = val;
  console.log("WebSocket message recieved...");
  console.log(event);
  const data = JSON.parse(event.data);
  if(data.from == selectedUser) {
    const three_dots = document.querySelector('.snippet');
    if(three_dots) {
      three_dots.className = 'snippet display-dots';
      const myTimeout = setTimeout(()=>{
        if(val == temp){
          three_dots.className = 'snippet hide-dots';
          val = 0;
        }
      }, 1500);
    }
  }

  try {
    if (data.type >= 0) receiveData(data.from, data.type, data.msg);
    else if (data.type == -1) receiveVideoCallData(data.msg);
  } catch (error) {
    console.log("Error while receiving ws message: " + error.message);
  }
};
ws.onerror = (event) => {
  console.log("WebSocket error occured...");
  console.log(event);
};
ws.onclose = (event) => {
  console.log("WebSocket connection closed...");
  console.log(event);
};

const sendWsData = (to, type, msg) => {
  data = JSON.stringify({ to: to, type: type, msg: msg });
  ws.send(data);
};
