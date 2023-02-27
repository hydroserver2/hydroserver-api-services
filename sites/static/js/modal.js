let modal = document.getElementById("add-sensor-modal");
document.getElementById("add-sensor-button").onclick = function()  { modal.style.display = "block";};
document.getElementsByClassName("close")[0].onclick = function() { modal.style.display = "none"; };
window.onclick = function(event) { if (event.target === modal) modal.style.display = "none";};

// Only show manufacturer and model if we're dealing with an instrumentDeployment
let sensorDropdown = document.getElementById("id_method_type");
let manufacturerField = document.getElementById("manufacturer-field");
let modelField = document.getElementById("model-field");
manufacturerField.style.display = "none";
modelField.style.display = "none";
sensorDropdown.onchange = function() {
  if (sensorDropdown.value === "instrumentDeployment") {
    manufacturerField.style.display = "block";
    modelField.style.display = "block";
  } else {
    manufacturerField.style.display = "none";
    modelField.style.display = "none";
  }
};

// Add new method to drop down list
let submit_btn = document.getElementById("submit-sensor-data");
let form = document.getElementById("add-sensor-form");
form.addEventListener("submit", function(event) {
    event.preventDefault();
    let csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    fetch(submit_btn.dataset.url, {
        method: "POST",
        headers: {"X-CSRFToken": csrftoken,},
        body: new FormData(form),
    })
    .then(response => {
        if (response.ok)
            return response.json();
        else
            throw new Error("Network response was not ok");
    })
    .then(data => {
        modal.style.display = "none";
        window.location.reload();
    })
    .catch(error => { console.error("Error adding sensor:", error);});
});