const rateAppointment = async (meetId, btn) => {
  showBtnLoading(btn);
  const result = await getFromServer(`/meetings/appointment/${meetId}/rating`);
  hideBtnLoading(btn);
  if (result.status) {
    data = result.data;
    if (result.data.user_rating) {
      const starsHtml =
        '<li class="list-inline-item me-0"><i class="fas fa-star text-warning"></i></li>'.repeat(
          data.user_rating.stars
        ) +
        '<li class="list-inline-item me-0 small"><i class="far fa-star text-warning"></i></li>'.repeat(
          5 - data.user_rating.stars
        );
      document.getElementById("user-review").innerHTML = `
        <p>${starsHtml}<p>
        <p>${data.user_rating.text}<p>
      `;
    } else {
      document.getElementById("user-review").innerHTML = `
        <input type="hidden" id="user_appoint_id" value="${meetId}">
        <!-- Question -->
        <div class="col-12 mt-2">
            <select id="user_stars" class="form-control" required>
            <option value="">Choose stars</option>
            <option value="5">★★★★★ (5/5)</option>
            <option value="4">★★★★☆ (4/5)</option>
            <option value="3">★★★☆☆ (3/5)</option>
            <option value="2">★★☆☆☆ (2/5)</option>
            <option value="1">★☆☆☆☆ (1/5)</option>
            </select>
        </div>
        <!-- Question -->
        <div class="col-12 mt-3">
            <textarea id="user_review" class="form-control" rows="3" required placeholder="Write some review...."></textarea>
        </div>
        <!-- Button -->
        <div class="col-12 mt-3" style="text-align: end;">
            <button type="submit" class="btn btn-success-soft my-0" id="user-review-btn">Post Review</button>
        </div>
        `;
    }
    if (result.data.appoint_rating) {
      const starsHtml =
        '<li class="list-inline-item me-0"><i class="fas fa-star text-warning"></i></li>'.repeat(
          data.appoint_rating.stars
        ) +
        '<li class="list-inline-item me-0 small"><i class="far fa-star text-warning"></i></li>'.repeat(
          5 - data.appoint_rating.stars
        );
      document.getElementById("appoint-review").innerHTML = `
        <p>${starsHtml}<p>
        <p>${data.appoint_rating.text}<p>
      `;
    } else {
      document.getElementById("appoint-review").innerHTML = `
        <input type="hidden" id="appoint_appoint_id" value="${meetId}">
        <!-- Question -->
        <div class="col-12 mt-2">
            <select id="appoint_stars" class="form-control" required>
            <option value="">Choose stars</option>
            <option value="5">★★★★★ (5/5)</option>
            <option value="4">★★★★☆ (4/5)</option>
            <option value="3">★★★☆☆ (3/5)</option>
            <option value="2">★★☆☆☆ (2/5)</option>
            <option value="1">★☆☆☆☆ (1/5)</option>
            </select>
        </div>
        <!-- Question -->
        <div class="col-12 mt-3">
            <textarea id="appoint_review" class="form-control" rows="3" required placeholder="Write some review...."></textarea>
        </div>
        <!-- Button -->
        <div class="col-12 mt-3" style="text-align: end;">
            <button type="submit" class="btn btn-success-soft my-0" id="appoint-review-btn">Post Review</button>
        </div>
        `;
    }
    new bootstrap.Modal(
      document.getElementById("appointmentReviewModal")
    ).show();
  } else {
    alertify.error(result.msg);
  }
};
const submitUserReview = async () => {
  const btn = document.getElementById("user-review-btn");
  const appoint_id = document.getElementById("user_appoint_id").value;
  showBtnLoading(btn);
  const result = await postToServer(
    `/meetings/appointment/${appoint_id}/rating`,
    {
      type: "user",
      stars: document.getElementById("user_stars").value,
      text: document.getElementById("user_review").value,
    }
  );
  hideBtnLoading(btn);
  if (result.status) {
    const starsHtml =
      '<li class="list-inline-item me-0"><i class="fas fa-star text-warning"></i></li>'.repeat(
        result.data.stars
      ) +
      '<li class="list-inline-item me-0 small"><i class="far fa-star text-warning"></i></li>'.repeat(
        5 - result.data.stars
      );
    document.getElementById("user-review").innerHTML = `
      <p>${starsHtml}<p>
      <p>${result.data.text}<p>
    `;
    alertify.success(result.msg);
  } else {
    alertify.error(result.msg);
  }
};
const submitAppointReview = async () => {
  const btn = document.getElementById("appoint-review-btn");
  const appoint_id = document.getElementById("appoint_appoint_id").value;
  showBtnLoading(btn);
  const result = await postToServer(
    `/meetings/appointment/${appoint_id}/rating`,
    {
      type: "appoint",
      stars: document.getElementById("appoint_stars").value,
      text: document.getElementById("appoint_review").value,
    }
  );
  hideBtnLoading(btn);
  if (result.status) {
    const starsHtml =
        '<li class="list-inline-item me-0"><i class="fas fa-star text-warning"></i></li>'.repeat(
          result.data.stars
        ) +
        '<li class="list-inline-item me-0 small"><i class="far fa-star text-warning"></i></li>'.repeat(
          5 - result.data.stars
        );
      document.getElementById("appoint-review").innerHTML = `
        <p>${starsHtml}<p>
        <p>${result.data.text}<p>
      `;
    alertify.success(result.msg);
  } else {
    alertify.error(result.msg);
  }
};
