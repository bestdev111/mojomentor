console.log("video-call.js");

// video calling
var localStream = new MediaStream();
const constraints = { video: true, audio: true };

const localVideo = document.getElementById("local-video");
// console.log(localVideo);
var userMedia = navigator.mediaDevices
  .getUserMedia(constraints)
  .then((stream) => {
    // console.log(stream);
    localStream = stream;
    localVideo.srcObject = localStream;
    localVideo.muted = true;
  })
  .catch((error) => {
    console.log("Error while accessing media devices.", error);
  });

const createOfferer = () => {
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
  var peer = new RTCPeerConnection(configuration);
  addLocalTracks(peer);
  var dc = peer.createDataChannel("channel");
  dc.addEventListener("open", () => {
    console.log("connection opened.");
  });
  dc.addEventListener("message", dcOnMessage);
  var remoteVideo = createVideo();
  setOnTrack(peer, remoteVideo);
  peer.createOffer((offer) => {
    console.log(offer);
  }, (error) => console.log(error))
  // console.log(peer);
};

const addLocalTracks = (peer) => {
  console.log(localStream.getTracks());
  localStream.getTracks().forEach((track) => {
    peer.addTrack(track, localStream);
  });
};

const dcOnMessage = (event) => {
  console.log(event.data);
};

const createVideo = () => {
  const videoHtml = `<video id="remote-video" autoplay></video>`;
  document
    .getElementById("video-box")
    .insertAdjacentHTML("beforeend", videoHtml);
  return document.getElementById("remote-video");
};
const setOnTrack = (peer, remoteVideo) => {
  var remoteStream = new MediaStream();
  remoteVideo.srcObject = remoteStream;
  peer.addEventListener("track", async (event) => {
    remoteStream.addTrack(event.track, remoteStream);
  });
};

createOfferer();
