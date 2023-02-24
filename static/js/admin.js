// --------------- Constants & Variables ---------------
const STATUS = ["InActive", "Active"];
const PERMISSION = ["No", "Yes"];
const APPROVAL = ["Pending", "Active", "InActive"];
// ---------------- data table rendering ----------------
// var category = document.getElementById("category");
const search = document.getElementById("search");
const pageIncBtn = document.getElementById("next_page");
const pageDecBtn = document.getElementById("back_btn");
var oldSearch = "";
// var oldCategory = "";
var pageNo = 0;
var rowCount = 10;
var pageAvail = 0;
const loadingData = `
    <div class="spinner-border m-auto my-5 d-block" id="loader">
      <span class="visually-hidden">Loading...</span>
    </div>`;
const renderTable = async () => {
  document.querySelector("#data-table tbody").innerHTML = loadingData;
//   if (search.value != oldSearch || category.value != oldCategory) {
  if (search.value != oldSearch) {
    pageNo = 0;
    oldSearch = search.value;
    // oldCategory = category.value;
  }
//   let params = `?search=${search.value}&category=${category.value}&no_of_row=${rowCount}&offset=${rowCount * pageNo}`;
  let params = `?search=${search.value}&no_of_row=${rowCount}&offset=${rowCount * pageNo}`;
  const res = await fetch(listUrl + params, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  });
  if (res.status === 200) {
    const data = (await res.json()).data;
    let rowsAvail = data.rows.length;
    const status = data.status ? data.status : null;
    const hidden = data.hidden ? data.hidden : [];
    const date_times = data.date_times ? data.date_times : [];

    let headHtml = "";
    let dataHtml = "";
    let rowHtml = "";
    data.columns.forEach((element, index) => {
      if (index !== 0 && !hidden.includes(index)) {
        headHtml += `<th>${element.replaceAll("_", " ").toUpperCase()}</th>`;
      }
    });
    headHtml = `<tr><th>S. No</th>${headHtml}${
      actions ? "<th>ACTION</th>" : ""
    }</tr>`;
    if (rowsAvail > 0) {
      data.rows.forEach((row, rowIndex) => {
        rowHtml = "";
        row.forEach((element, index) => {
          if (index !== 0 && !hidden.includes(index)) {
            if (status === index)
              rowHtml += `<td>${element === true ? 'Active' : 'InActive'}</td>`;
            else if (date_times.includes(index))
              rowHtml += `<td>${element ? fromatToDateTime(element.split('.')[0]) : '--'}</td>`;
            else rowHtml += `<td>${element}</td>`;
          }
        });
        if (actions) rowHtml += `<td id="act-${row[0]}">${actions(row)}</td>`;
        dataHtml +=
          `<tr id="${row[0]}"><td>${rowIndex + 1}</td>` + rowHtml + "</tr>";
      });
    }
    document.querySelector("#data-table thead").innerHTML = headHtml;
    document.querySelector("#data-table tbody").innerHTML = dataHtml;
    pageAvail = parseInt(data.count / rowCount);
    pageDecBtn.disabled = pageNo > 0 ? false : true;
    pageIncBtn.disabled = pageNo < pageAvail ? false : true;
    document.getElementById("page-no").innerHTML = pageNo + 1;
    document.getElementById("entries_details").innerHTML = `Showing ${
      rowCount * pageNo + 1
    } to ${rowCount * pageNo + rowsAvail} of ${data.count} entries`;
  } else {
    document.getElementById("questions").innerHTML = "";
  }
};
const decreasePage = () => {
  if (pageNo > 0) {
    pageNo--;
    renderTable();
  }
};
const increasePage = () => {
  if (pageNo < pageAvail) {
    pageNo++;
    renderTable();
  }
};
// --------------- Call table reload ---------------
if (typeof needTable !== 'undefined' && needTable) renderTable();
