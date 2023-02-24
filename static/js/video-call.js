console.log("video-call.js");

const configuration = {
  iceServers: [
    { urls: ["stun:stun.l.google.com:19302", "stun:stun1.l.google.com:19302"] },
    // {
    //   url: "turn:numb.viagenie.ca",
    //   credential: "muazkh",
    //   username: "webrtc@live.com",
    // },
    // {
    //   url: "turn:192.158.29.39:3478?transport=udp",
    //   credential: "JZEOEt2V3Qb0y27GRntt2u2PAYA=",
    //   username: "28224511:1379330808",
    // },
  ],
};

// video calling
var localStream = new MediaStream();
const constraints = { video: true, audio: true };

var peer = new RTCPeerConnection(configuration);
var dc = peer.createDataChannel("channel");

const localVideo = document.getElementById("local-video");
const remoteVideo = document.getElementById("remote-video");
// console.log(localVideo);
var userMedia = navigator.mediaDevices
  .getUserMedia(constraints)
  .then((stream) => {
    // console.log(stream);
    localStream = stream;
    localVideo.srcObject = localStream;
    localVideo.muted = true;
    peer.addStream(localStream);
  })
  .catch((error) => {
    console.log("Error while accessing media devices.", error);
  });

dc.addEventListener("open", () => {
  console.log("connection opened.");
});

dc.addEventListener("message", (event) => {
  console.log(event.data);
});


peer.onicecandidate = (e) => {
  if(e.candidate == null) return;
  // console.log(e.candidate); // need to send it to server as candidate
  sendWsData(toUser, -1, {info_type: 'candidate', candidate: e.candidate});
}

peer.onaddstream = (e) => {
  remoteVideo.srcObject = e.stream;
}

const startCall = () => {
  peer.createOffer(offer => {
    peer.setLocalDescription(offer);
    sendWsData(toUser, -1, {info_type: 'offer', offer: offer});
  }, (error) => console.log(error)).then(a => console.log("set successfully."));

}

const receiveVideoCallData = (data) => {
  if(data.info_type == 'offer') {
    peer.setRemoteDescription(data.offer);
    peer.createAnswer(answer => {
      peer.setLocalDescription(answer);
      sendWsData(toUser, -1, {info_type: 'answer', answer: answer});
    }, (error) => console.log(error)).then(a => console.log("set successfully."))
  } else if(data.info_type == 'answer') {
    peer.setRemoteDescription(data.answer);
    console.log("answer");
  } else if(data.info_type == 'candidate') {
    peer.addIceCandidate(data.candidate);
    console.log("candidate")
  }
}