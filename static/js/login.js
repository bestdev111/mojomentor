// --------------- login using google ---------------
window.onload = function () {
  google.accounts.id.initialize({
    client_id: G_CLIENT_ID,
    callback: handleCredentialResponse,
    cancel_on_tap_outside: false,
  });
  google.accounts.id.renderButton(
    document.getElementById("buttonDiv"),
    {
      theme: "filled_blue",
      size: "large",
      shape: "rectangular",
      text: "continue_with",
    } // customization attributes
  );
  google.accounts.id.prompt(); // also display the One Tap dialog
};
async function handleCredentialResponse(response) {
  // console.log("Encoded JWT ID token: " + response.credential);
  const result = await postToServer("/login-using-google", { credential: response.credential });
  if (result.status) {
    if(result.data && result.data.role) {
      if(result.data.role == 1) window.location.href = "/admin/dashboard";
      if(result.data.role == 2) window.location.href = "/admin/dashboard";
      if(result.data.role == 3) window.location.href = "/instructor/dashboard";
      if(result.data.role == 4) window.location.href = "/student/dashboard";
    } else {
      window.location.href = "/"
    }
  } else alertify.error(result.msg);
}

// --------------- initiating facebook ---------------
window.fbAsyncInit = function () {
  FB.init({
    appId: F_APP_ID,
    cookie: true,
    xfbml: true,
    version: "v14.0",
  });

  FB.AppEvents.logPageView();
  //   FB.getLoginStatus(function (response) {
  //     console.log(response);
  //   });
};

(function (d, s, id) {
  var js,
    fjs = d.getElementsByTagName(s)[0];
  if (d.getElementById(id)) {
    return;
  }
  js = d.createElement(s);
  js.id = id;
  js.src = "https://connect.facebook.net/en_US/sdk.js";
  fjs.parentNode.insertBefore(js, fjs);
})(document, "script", "facebook-jssdk");

// function checkLoginState() {
//   FB.getLoginStatus(function (response) {
//     console.log(response);
//   });
// }
// --------------- login using facebook ---------------
const fbLogin = (btn) => {
  FB.login(
    function (response) {
      if (response.status === "connected") {
        sendFacebookDataToServer(response.authResponse, btn);
      } else {
        showAlert(
          "Login using Facebook",
          "Please grant permission on facebook login"
        );
      }
    },
    { scope: "public_profile,email" }
  );
};
// --------------- hit own server for login using facebook ---------------
const sendFacebookDataToServer = async (fbObj, btn) => {
  // startLoading();
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
  btn.setAttribute("disabled", true);
  
  const result = await postToServer("/login-using-facebook", fbObj);

  // stopLoading();
  btn.innerHTML =
    '<i class="fa-brands fa-facebook-square"></i> Continue with FaceBook';
  btn.removeAttribute("disabled");

  if (result.status) {
    if(result.data && result.data.role) {
      if(result.data.role == 1) window.location.href = "/admin/dashboard";
      if(result.data.role == 2) window.location.href = "/admin/dashboard";
      if(result.data.role == 3) window.location.href = "/instructor/dashboard";
      if(result.data.role == 4) window.location.href = "/student/dashboard";
    } else {
      window.location.href = "/"
    }
  } else alertify.error(result.msg);
};
