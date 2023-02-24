// --------------- upload lecture ---------------
const uploadLecture = async (btn, courseId) => {
  const lectureName = document.getElementById("lecture_name");
  if (lectureName.value == "") {
    lectureName.style.borderColor = "red";
    return;
  } else lectureName.style.borderColor = "#dde0e3";
  showBtnLoading(btn);
  const data = { name: lectureName.value };
  const res = await postToServer(
    `/instructor/course/${courseId}/lecture/create`,
    data
  );
  hideBtnLoading(btn);
  if (res.status) {
    lectureName.value = "";
    alertify.success(res.msg);
    document.getElementById("closeAddLecture").click();
    appendLecture(res.data.id, data.name);
  } else {
    alertify.error(res.msg);
  }
};
// --------------- upload CourseFaq ---------------
const uploadCourseFaq = async (btn, courseId) => {
  const courseFaqQues = document.getElementById("course_faq_ques");
  const courseFaqAns = document.getElementById("course_faq_ans");
  let error = false;
  if (courseFaqQues.value == "") {
    courseFaqQues.style.borderColor = "red";
    error = true;
  } else courseFaqQues.style.borderColor = "#dde0e3";
  if (courseFaqAns.value == "") {
    courseFaqAns.style.borderColor = "red";
    error = true;
  } else courseFaqAns.style.borderColor = "#dde0e3";
  if (error) return false;
  showBtnLoading(btn);
  const data = { question: courseFaqQues.value, answer: courseFaqAns.value };
  const res = await postToServer(
    `/instructor/course/${courseId}/course-faq/create`,
    data
  );
  hideBtnLoading(btn);
  if (res.status) {
    courseFaqQues.value = courseFaqAns.value = "";
    alertify.success(res.msg);
    document.getElementById("closeAddFAQ").click();
    appendCourseFaq(res.data.id, data.question, data.answer);
  } else {
    alertify.error(res.msg);
  }
};
// --------------- upload CourseFaq ---------------
const uploadCourseMedia = async (btn, courseId) => {
  const courseImage = document.getElementById("course_image");
  const courseVideo = document.getElementById("course_video");
  let error = false;
  if (courseImage.value == "") {
    courseImage.style.borderColor = "red";
    error = true;
  } else courseImage.style.borderColor = "#dde0e3";
  if (courseVideo.value == "") {
    courseVideo.style.borderColor = "red";
    error = true;
  } else courseVideo.style.borderColor = "#dde0e3";
  if (error) return false;
  showBtnLoading(btn);
  const formData = new FormData();
  formData.append("image", courseImage.files[0]);
  formData.append("video", courseVideo.files[0]);
  const res = await postFormToServer(
    `/instructor/course/${courseId}/media`,
    formData
  );
  hideBtnLoading(btn);
  res.status ? alertify.success(res.msg) : alertify.error(res.msg);
};

// --------------- update topic popup ---------------
const saveTopicBtn = document.getElementById("saveTopicBtn");
const updateTopicPopup = (lecture_id) => {
  saveTopicBtn.onclick = () => uploadTopic(saveTopicBtn, lecture_id);
};
// --------------- upload topic ---------------
const uploadTopic = async (btn, lectureId) => {
  const topicName = document.getElementById("topic_name");
  const topicVideo = document.getElementById("topic_video");
  const topicDescrip = document.getElementById("topic_description");
  let error = false;
  if (topicName.value == "") {
    topicName.style.borderColor = "red";
    error = true;
  } else topicName.style.borderColor = "#dde0e3";
  if (topicVideo.value == "") {
    topicVideo.style.borderColor = "red";
    error = true;
  } else topicVideo.style.borderColor = "#dde0e3";
  if (topicDescrip.value == "") {
    topicDescrip.style.borderColor = "red";
    error = true;
  } else topicDescrip.style.borderColor = "#dde0e3";
  if (error) return false;
  const premium = document.getElementById("premium_yes").checked ? 1 : 0;
  const formData = new FormData();
  formData.append("video", topicVideo.files[0]);
  formData.append("name", topicName.value);
  formData.append("description", topicDescrip.value);
  formData.append("premium", premium);
  showBtnLoading(btn);
  const res = await postFormToServer(
    `/instructor/lecture/${lectureId}/topic/create`,
    formData
  );
  hideBtnLoading(btn);
  if (res.status) {
    topicName.value = topicVideo.value = topicDescrip.value = "";
    alertify.success(res.msg);
    saveTopicBtn.onclick = "";
    document.getElementById("closeAddTopic").click();
    appendTopic(res.data.id, formData.get("name"), lectureId);
  } else {
    alertify.error(res.msg);
  }
};
// --------------- updating dome ---------------
const appendTopic = (id, name, lectureId) => {
  const content = `
  <!-- Video item START -->
  <div class="d-flex justify-content-between align-items-center">
    <div class="position-relative">
      <a
        href="#"
        class="btn btn-danger-soft btn-round btn-sm mb-0 stretched-link position-static"
        ><i class="fas fa-play"></i
      ></a>
      <span class="ms-2 mb-0 h6 fw-light">${name}</span>
    </div>
    <!-- Edit and cancel button -->
    <div>
      <a
        href="#"
        class="btn btn-sm btn-success-soft btn-round me-1 mb-1 mb-md-0"
        ><i class="far fa-fw fa-edit"></i
      ></a>
      <button class="btn btn-sm btn-danger-soft btn-round mb-0">
        <i class="fas fa-fw fa-times"></i>
      </button>
    </div>
  </div>
  <!-- Divider -->
  <hr />
  <!-- Video item END -->
  `;
  console.log("topic-box-" + lectureId);
  console.log(document.getElementById("topic-box-" + lectureId));
  document
    .getElementById("topic-box-" + lectureId)
    .insertAdjacentHTML("beforeend", content);
};
const appendLecture = (id, name) => {
  const lectureNo =
    document.querySelectorAll("#lecture-box > .accordion-item").length + 1;
  const content = `
  <!-- Item START -->
  <div class="accordion-item mb-3">
    <h6 class="accordion-header font-base" id="heading-${lectureNo}">
      <button
        class="accordion-button fw-bold rounded d-inline-block collapsed d-block pe-5"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#collapse-${lectureNo}"
        aria-expanded="false"
        aria-controls="collapse-${lectureNo}"
      >
        ${name}
      </button>
    </h6>

    <div
      id="collapse-${lectureNo}"
      class="accordion-collapse collapse"
      aria-labelledby="heading-${lectureNo}"
      data-bs-parent="#accordionExample2"
    >
      <!-- Topic START -->
      <div class="accordion-body mt-3">
        <div id="topic-box-${id}">
          
        </div>
        <!-- Add topic -->
        <a
          href="javascript:void(0);"
          onclick="updateTopicPopup(${id})"
          class="btn btn-sm btn-dark mb-0"
          data-bs-toggle="modal"
          data-bs-target="#addTopic"
          >
          <i class="bi bi-plus-circle me-2"></i>Add topic
        </a>
      </div>
      <!-- Topic END -->
    </div>
  </div>
  <!-- Item END -->
  `;
  document
    .getElementById("lecture-box")
    .insertAdjacentHTML("beforeend", content);
};
const appendCourseFaq = (id, ques, ans) => {
  const content = `
  <div class="col-12">
    <div class="bg-body p-3 p-sm-4 border rounded">
      <!-- Item 1 -->
      <div
        class="d-sm-flex justify-content-sm-between align-items-center mb-2"
      >
        <!-- Question -->
        <h6 class="mb-0">${ques}</h6>
        <!-- Button -->
        <div class="align-middle">
          <a
            href="#"
            class="btn btn-sm btn-success-soft btn-round me-1 mb-1 mb-md-0"
            ><i class="far fa-fw fa-edit"></i
          ></a>
          <button
            class="btn btn-sm btn-danger-soft btn-round mb-0"
          >
            <i class="fas fa-fw fa-times"></i>
          </button>
        </div>
      </div>
      <!-- Content -->
      <p>${ans}</p>
    </div>
  </div>
  `;
  document
    .getElementById("course-faq-box")
    .insertAdjacentHTML("beforeend", content);
};
