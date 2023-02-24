// -------------------- Notifications --------------------
const messages = document.getElementById("messages").children;
const total = messages.length;
let message;
for (let i = 0; i < total; i++) {
  message = messages[i].innerHTML.split("||||");
  if (message[0] === "success") alertify.success(message[1]);
  else if (message[0] === "error") alertify.error(message[1]);
}
// -------------------- Alerts --------------------
const showAlert = (head, msg, field = null) => {
  alertify.alert(msg, function () {}).setHeader("<em> " + head + " </em> ");
};
// --------------- phone number validator ---------------
const validatePhoneNo = (e, obj) => {
  var x = e.which || e.keycode;
  if (x >= 48 && x <= 57 && obj.value.length < 10) return true;
  else return false;
};
// --------------- percentage validator ---------------
const validatePercentage = (e, obj) => {
  var x = e.which || e.keycode;
  if (x >= 48 && x <= 57 && obj.value.length < 2) return true;
  else return false;
};
// --------------- button loading ---------------
const showBtnLoading = (btn) => {
  if (!btn) return;
  btn.setAttribute("data-html", btn.innerHTML);
  btn.setAttribute("disabled", true);
  btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
};
const hideBtnLoading = (btn) => {
  if (!btn) return;
  btn.innerHTML = btn.getAttribute("data-html");
  btn.removeAttribute("disabled");
};
const showBtnLoading2 = (btn) => {
  if (!btn) return;
  btn.setAttribute("data-html", btn.innerHTML);
  btn.setAttribute("disabled", true);
  btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
};
const hideBtnLoading2 = (btn) => {
  if (!btn) return;
  btn.innerHTML = btn.getAttribute("data-html");
  btn.removeAttribute("disabled");
};
// --------------- mins to time time in HH:MM ---------------
const minsToHHMM = (mins) => {
  if (mins > 1440) mins = mins - 1440;
  return `${String(mins / 60).padStart(2, '0')}:${String(mins % 60).padStart(2, '0')}`;
};
const hhMMTomins = (timeStr) => {
  const timeArr = timeStr.split(':');
  return (parseInt(timeArr[0]) * 60) + parseInt(timeArr[1])
}
// --------------- time zons ---------------
const utcOffset = document.querySelector('meta[name="utc-offset"]').content;
const utcOffsetVal = [];
if(utcOffset) {
  utcOffsetVal.push(utcOffset[0]);
  const hr_min = utcOffset.slice(1, 6).split(":");
  utcOffsetVal.push(hr_min[0]);
  utcOffsetVal.push(hr_min[1]);
}
const fromatToDateTime = (datetimeStr) => {
  let dt;
  if (utcOffset) {
    if (utcOffsetVal[0] == '+') dt = Date.parse(datetimeStr).add({ hours: utcOffsetVal[1], minutes: utcOffsetVal[2] });
    else dt = Date.parse(datetimeStr).subtract({ hours: utcOffsetVal[1], minutes: utcOffsetVal[2] });
  }
  else dt = Date.parse(datetimeStr);
  return dt.toString("ddd, MMM d, yyyy HH:mm:ss");
}
const fromatToDateAndTime = (datetimeStr) => {
  let dt;
  if (utcOffset) {
    if (utcOffsetVal[0] == '+') dt = Date.parse(datetimeStr).add({ hours: utcOffsetVal[1], minutes: utcOffsetVal[2] });
    else dt = Date.parse(datetimeStr).subtract({ hours: utcOffsetVal[1], minutes: utcOffsetVal[2] });
  }
  else dt = Date.parse(datetimeStr);
  return [dt.toString("ddd, MMM d, yyyy"), dt.toString("HH:mm:ss")];
}
const formatToTime = (timeStr) => {
  let dt;
  if (utcOffset) {
    if (utcOffsetVal[0] == '+') dt = Date.parse(timeStr).add({ hours: utcOffsetVal[1], minutes: utcOffsetVal[2] });
    else dt = Date.parse(timeStr).subtract({ hours: utcOffsetVal[1], minutes: utcOffsetVal[2] });
  }
  else dt = Date.parse(timeStr);
  return dt.toString("HH:mm:ss");
}

const toDateAndTime = (datetimeStr) => {
  let dt;
  if (utcOffset) {
    if (utcOffsetVal[0] == '+') dt = Date.parse(datetimeStr).add({ hours: utcOffsetVal[1], minutes: utcOffsetVal[2] });
    else dt = Date.parse(datetimeStr).subtract({ hours: utcOffsetVal[1], minutes: utcOffsetVal[2] });
  }
  else dt = Date.parse(datetimeStr);
  return [dt.toString("yyyy-MM-dd"), dt.toString("HH:mm")];
}
const toTime = (timeStr) => {
  let dt;
  if (utcOffset) {
    if (utcOffsetVal[0] == '+') dt = Date.parse(timeStr).add({ hours: utcOffsetVal[1], minutes: utcOffsetVal[2] });
    else dt = Date.parse(timeStr).subtract({ hours: utcOffsetVal[1], minutes: utcOffsetVal[2] });
  }
  else dt = Date.parse(timeStr);
  return dt.toString("HH:mm");
}