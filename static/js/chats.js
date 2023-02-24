const emojis = [
  0x1f600, 0x1f603, 0x1f604, 0x1f601, 0x1f606, 0x1f605, 0x1f923, 0x1f602,
  0x1f642, 0x1f643, 0x1fae0, 0x1f609, 0x1f60a, 0x1f607, 0x1f970, 0x1f60d,
  0x1f929, 0x1f618, 0x1f617, 0x263a, 0x1f61a, 0x1f619, 0x1f972, 0x1f60b,
  0x1f61b, 0x1f61c, 0x1f92a, 0x1f61d, 0x1f911, 0x1f917, 0x1f92d, 0x1fae2,
  0x1fae3, 0x1f92b, 0x1f914, 0x1fae1, 0x1f910, 0x1f928, 0x1f610, 0x1f611,
  0x1f636, 0x1fae5, 0x1f636, 0x200d, 0x1f32b, 0xfe0f, 0x1f60f, 0x1f612, 0x1f644,
  0x1f62c, 0x1f62e, 0x200d, 0x1f4a8, 0x1f925, 0x1f60c, 0x1f614, 0x1f62a,
  0x1f924, 0x1f634, 0x1f637, 0x1f912, 0x1f915, 0x1f922, 0x1f92e, 0x1f927,
  0x1f975, 0x1f976, 0x1f974, 0x1f635, 0x1f635, 0x200d, 0x1f4ab, 0x1f92f,
  0x1f920, 0x1f973, 0x1f978, 0x1f60e, 0x1f913, 0x1f9d0, 0x1f615, 0x1fae4,
  0x1f61f, 0x1f641, 0x2639, 0x1f62e, 0x1f62f, 0x1f632, 0x1f633, 0x1f97a,
  0x1f979, 0x1f626, 0x1f627, 0x1f628, 0x1f630, 0x1f625, 0x1f622, 0x1f62d,
  0x1f631, 0x1f616, 0x1f623, 0x1f61e, 0x1f613, 0x1f629, 0x1f62b, 0x1f971,
  0x1f624, 0x1f621, 0x1f620, 0x1f92c, 0x1f608, 0x1f47f,
];
let html = "";
for (let i = 0; i < emojis.length; i++) {
  const emoji = emojis[i];
  html += `<button class="emoji" onclick="selectEmoji(${emoji})">${String.fromCodePoint(
    emoji
  )}</button>`;
}
document.getElementById("emojis").innerHTML = html;
const selectEmoji = (emoji) => {
  msgField.value = msgField.value + String.fromCodePoint(emoji);
  msgField.focus();
};

const chatAudio = new Audio("/static/sounds/chats.wav");
const playSound = () => chatAudio.play().catch(function(error) {console.log(error.message);});

// websocket dom code
const sendData = (to, type, msg) => {
  // console.log('====>', type);
  const chatsBox = document.getElementById("chats-" + to);
  sendWsData(to, type, msg);
  if(type !== -1) {
    renderChat(chatsBox, 'send', type, msg, to);
  }
  chatsBox.scrollTop = chatsBox.scrollHeight;
};
const receiveData = (from, type, msg) => {
  const chatsBox = document.getElementById("chats-" + from);
  renderChat(chatsBox, 'receive', type, msg, from);
  chatsBox.scrollTop = chatsBox.scrollHeight;
  if (to !== from) {
    const user = document.querySelector(`#u-${from} .uname`);
    const title = user ? user.innerHTML : "";
    showToast(title, msg);
  }
  playSound();
  console.log("Hellos");
};
const showToast = (title, msg) => {
  const html = `
  <div class="toast show" role="alert" aria-live="assertive" aria-atomic="true">
    <div class="toast-header">
      <!-- <img src="..." class="rounded me-2" alt="${title}"> -->
      <strong class="me-auto">${title}</strong>
      <small>11 mins ago</small>
      <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>
    <div class="toast-body">
      ${msg}
    </div>
  </div>`;
  document.getElementById("toasts").insertAdjacentHTML("beforeend", html);
};
const loadChats = async (user_id) => {
  document.getElementById("three_dots").innerHTML = `
    <div class="snippet hide-dots" data-title="dot-flashing">
      <div class="stage">
        <div class="dot-flashing"></div>
      </div>
    </div>
  `
  msgField.setAttribute("disabled", true);
  sendBtn.setAttribute("disabled", true);
  const result = await getFromServer("/account/get-chats/" + user_id);
  const chatsBox = document.getElementById("chats-" + user_id)
  result.data.rows.forEach((chat) => {
    renderChat(chatsBox, chat[0], chat[1], chat[2], user_id);
  });
  chatsBox.scrollTop = chatsBox.scrollHeight;
  msgField.removeAttribute("disabled");
  sendBtn.removeAttribute("disabled");
};
const renderChat = (chatsBox, msg_side, msg_type, msg, user_id) => {
  let profileImg = document.getElementById(`profile-${user_id}`);
	profileImg = (profileImg && profileImg.src) ? profileImg.src : '/static/images/user.png';

  const msgHtmlText = msg.replace(/(?:\r\n|\r|\n)/g, '<br>');
  // if(msg_type == -1) {
  //   console.log('message?????');
  //   const three_dots = document.querySelector('.three-dots');
  //   three_dots.style.display = 'flex';
  //   setInterval(()=> {three_dots.style.display = 'none'}, 2000);
  // } else {
    if(msg_type == 1) {
      if (msg_side == 'receive') {
        html = `
        <div class="file receiver">
          <img src="${profileImg}" alt="avatar 1">
          <div>
            <h6>File <a href="/media/${msgHtmlText}" download target="_blank"><i class="fas fa-download"></i></a>
            </h6><p><a href="/media/${msgHtmlText}" target="_blank">${msgHtmlText}</a></p>
          </div>
        </div>`;
      } else {
        html = `
        <div class="file sender">
          <div>
            <h6>File <a href="/media/${msgHtmlText}" download target="_blank"><i class="fas fa-download"></i></a>
            </h6><p><a href="/media/${msgHtmlText}" target="_blank">${msgHtmlText}</a></p>
          </div>
          <img src="${currUserPic}" alt="avatar 1">
        </div>`;
      }
    } else {
      if (msg_side == 'receive') {
        html = `
        <div class="chat receiver">
          <img src="${profileImg}" alt="avatar 1">
          <div><p>${msgHtmlText}</p></div>
        </div>`;
      } else {
        html = `
        <div class="chat sender">
          <div><p>${msgHtmlText}</p></div>
          <img src="${currUserPic}" alt="avatar 1">
        </div>`;
      }
    }
    chatsBox.insertAdjacentHTML("beforeend", html); // afterbegin
  // }
}