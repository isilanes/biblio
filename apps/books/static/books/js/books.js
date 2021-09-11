$(document).ready(function() {
    slider = document.getElementById("slider");
    output = document.getElementById("pages-count");

    slider.oninput = function() {
        output.innerHTML = this.value;
    };

    output.innerHTML = slider.value;
});

function mytoggle(id) {
    var x = document.getElementById(id);
    if (x.style.display == "none") {
        x.style.display = "";
    } else {
        x.style.display = "none";
    }
};

function toggle_stats() {
    mytoggle('stats-stats-block');
    mytoggle('stats-progress-block');
};

function toggle_slider() {
    mytoggle("slider-block");
    mytoggle("update-button-block");
    mytoggle("save-button-block");
}