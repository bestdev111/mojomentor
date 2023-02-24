// --------------- global veriables ---------------
const token = document.querySelector('meta[name="csrf-token"]').content;
// --------------- post request ---------------
const postToServer = async (url, data = {}) => {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-CSRFToken": token },
    body: JSON.stringify(data),
  });
  const result = { msg: "Something went wrong.", status: false };
  if (res.redirected) {
    window.location.href = `${res.url.split("?")[0]}?next=${
      window.location.pathname
    }`;
  } else if (res.status === 403) {
    console.log("CSRF Token expired or missing");
  } else if (res.status === 200 || res.status === 201) {
    const jsonData = await res.json();
    result.status = true;
    result.msg = jsonData.msg;
    result.data = jsonData.data;
  } else {
    try {
      const msg = (await res.json()).msg;
      if (msg) result.msg = msg;
    } catch (err) {
      console.log(err);
    }
  }
  return result;
};
// --------------- post form data ---------------
const postFormToServer = async (url, data = new FormData()) => {
  const res = await fetch(url, {
    method: "POST",
    headers: {
      // "Content-Type": "multipart/form-data",
      "X-CSRFToken": token,
    },
    body: data,
  });
  const result = { msg: "Something went wrong.", status: false };
  if (res.redirected) {
    window.location.href = `${res.url.split("?")[0]}?next=${
      window.location.pathname
    }`;
  } else if (res.status === 403) {
    console.log("CSRF Token expired or missing");
  } else if (res.status === 200 || res.status === 201) {
    const jsonData = await res.json();
    result.status = true;
    result.msg = jsonData.msg;
    result.data = jsonData.data;
  } else {
    try {
      const msg = (await res.json()).msg;
      if (msg) result.msg = msg;
    } catch (err) {
      console.log(err);
    }
  }
  return result;
};
// --------------- get request ---------------
const getFromServer = async (url) => {
  const res = await fetch(url, {
    method: "GET",
    headers: { "Content-Type": "application/json", "X-CSRFToken": token },
  });
  const result = { msg: "Something went wrong.", status: false };
  if (res.redirected) {
    window.location.href = `${res.url.split("?")[0]}?next=${
      window.location.pathname
    }`;
  } else if (res.status === 403) {
    console.log("CSRF Token expired or missing");
  } else if (res.status === 200 || res.status === 201) {
    const jsonData = await res.json();
    result.status = true;
    result.msg = jsonData.msg;
    result.data = jsonData.data;
  } else {
    try {
      const msg = (await res.json()).msg;
      if (msg) result.msg = msg;
    } catch (err) {
      console.log(err);
    }
  }
  return result;
};
// --------------- file uploader with progress ---------------
const uploadFileForm = (url, formdata, progressHandler, completeHandler, errorHandler, abortHandler) => {
  const ajax = new XMLHttpRequest();
  ajax.upload.addEventListener("progress", progressHandler, false);
  ajax.addEventListener("load", completeHandler, false);
  ajax.addEventListener("error", errorHandler, false);
  ajax.addEventListener("abort", abortHandler, false);
  ajax.open("POST", url);
  ajax.setRequestHeader("X-CSRFToken", token)
  ajax.send(formdata);
}
