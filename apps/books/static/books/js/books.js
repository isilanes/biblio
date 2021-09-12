$(document).ready(function() {});

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