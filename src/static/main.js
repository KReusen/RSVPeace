window.onload = function () {
  set_people_spelling();
  disable_or_enable_submit_button();
};

const form = document.getElementById("rsvp_form");
const form_result_message = document.getElementById("form_result_message");

function set_people_spelling() {
  const n = document.getElementById("plusones").value;
  let word = "people";
  if (n == 1) {
    word = "person";
  }
  document.getElementById("people_spelling").innerText = word;
}

function show_success_message() {
  form_result_message.innerHTML = `
  <div class="alert alert-success alert-dismissible fade show" id="success-alert" role="alert">
  <strong>Success!</strong> You have updated your attendance.
  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
</div>`;
  setTimeout(function () {
    bootstrap.Alert.getOrCreateInstance(
      document.querySelector("#success-alert")
    ).close();
  }, 5000);
}

function show_error_message() {
  form_result_message.innerHTML = `
  <div class="alert alert-danger alert-dismissible fade show" id="failure-alert" role="alert">
  <strong>Error</strong> Something went wrong. Contact your host for assistance and explain what you were trying to do.
  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
</div>`;
  setTimeout(function () {
    bootstrap.Alert.getOrCreateInstance(
      document.querySelector("#failure-alert")
    ).close();
  }, 5000);
}

function disable_or_enable_submit_button() {
  const nothing_selected =
    !form.elements["yes"].checked && !form.elements["no"].checked;
  if (nothing_selected) {
    document.getElementById("update_rsvp_button").disabled = true;
  } else {
    document.getElementById("update_rsvp_button").disabled = false;
  }
}

// EVENT LISTENERS
// ---------------

// radio buttons
document.querySelectorAll('input[name="going"]').forEach(function (el) {
  el.addEventListener("click", function () {
    disable_or_enable_submit_button();
  });
});

// spelling
document.getElementById("plusones").onchange = () => {
  set_people_spelling();
};

// form submit
form.addEventListener("submit", (event) => {
  event.preventDefault();
  form_result_message.innerText = "";
  const going = form.elements["yes"].checked;
  const plusones = form.elements["plusones"].value;

  fetch(window.location.href, {
    method: "POST",
    body: JSON.stringify({ going, plusones }),
    headers: {
      "Content-type": "application/json; charset=UTF-8",
    },
  })
    .then((response) => {
      if (response.ok) {
        return show_success_message();
      }
      return Promise.reject(response);
    })
    .catch((_) => show_error_message());
});
