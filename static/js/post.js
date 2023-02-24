// --------------- global veriables ---------------
const token = document.querySelector('meta[name="csrf-token"]').content;
// --------------- like unlike ---------------
const likeQues = async (obj, id) => {
  const likes = obj.querySelector("span.likes");
  let likeCount = parseInt(likes.innerHTML);
  likeCount = likeCount ? likeCount : 0;
  let url;
  if (parseInt(obj.getAttribute("data-liked"))) {
    obj.setAttribute("data-liked", 0);
    obj.classList.remove("active");
    const subtractedLikes = likeCount - 1;
    likes.innerHTML = subtractedLikes ? subtractedLikes : "";
    url = `/post/question/${id}/unlike`;
  } else {
    obj.setAttribute("data-liked", 1);
    obj.classList.add("active");
    likes.innerHTML = likeCount + 1;
    url = `/post/question/${id}/like`;
  }
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": token,
    },
    // body: JSON.stringify({}),
  });
  if (res.status === 201 || res.status === 200) {
    console.log("hellos");
  }
};
// --------------- vote unvote ---------------
const voteAns = async (obj, id) => {
  const votes = obj.querySelector("span.votes");
  let voteCount = parseInt(votes.innerHTML);
  voteCount = voteCount ? voteCount : 0;
  let url;
  if (parseInt(obj.getAttribute("data-voted"))) {
    obj.setAttribute("data-voted", 0);
    obj.classList.remove("active");
    const subtractedVotes = voteCount - 1;
    votes.innerHTML = subtractedVotes ? subtractedVotes : "";
    url = `/post/answer/${id}/unvote`;
  } else {
    obj.setAttribute("data-voted", 1);
    obj.classList.add("active");
    votes.innerHTML = voteCount + 1;
    url = `/post/answer/${id}/vote`;
  }
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": token,
    },
    // body: JSON.stringify({}),
  });
  if (res.status === 201 || res.status === 200) {
    console.log("hellos");
  }
};
// --------------- endorse unendorse ---------------
const endorseAns = async (obj, id) => {
  const endorses = obj.querySelector("span.endorses");
  let endorseCount = parseInt(endorses.innerHTML);
  endorseCount = endorseCount ? endorseCount : 0;
  let url;
  if (parseInt(obj.getAttribute("data-endorsed"))) {
    obj.setAttribute("data-endorsed", 0);
    obj.classList.remove("active");
    const subtractedendorses = endorseCount - 1;
    endorses.innerHTML = subtractedendorses ? subtractedendorses : "";
    url = `/post/answer/${id}/unendorse`;
  } else {
    obj.setAttribute("data-endorsed", 1);
    obj.classList.add("active");
    endorses.innerHTML = endorseCount + 1;
    url = `/post/answer/${id}/endorse`;
  }
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": token,
    },
    // body: JSON.stringify({}),
  });
  if (res.status === 201 || res.status === 200) {
    console.log("hellos");
  }
};
// --------------- disapprove undisapprove ---------------
const disapproveAns = async (obj, id) => {
  const disapproves = obj.querySelector("span.disapproves");
  let disapproveCount = parseInt(disapproves.innerHTML);
  disapproveCount = disapproveCount ? disapproveCount : 0;
  let url;
  if (parseInt(obj.getAttribute("data-disapproved"))) {
    obj.setAttribute("data-disapproved", 0);
    obj.classList.remove("active");
    const subtracteddisapproves = disapproveCount - 1;
    disapproves.innerHTML = subtracteddisapproves ? subtracteddisapproves : "";
    url = `/post/answer/${id}/undisapprove`;
  } else {
    obj.setAttribute("data-disapproved", 1);
    obj.classList.add("active");
    disapproves.innerHTML = disapproveCount + 1;
    url = `/post/answer/${id}/disapprove`;
  }
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": token,
    },
    // body: JSON.stringify({}),
  });
  if (res.status === 201 || res.status === 200) {
    console.log("hellos");
  }
};
