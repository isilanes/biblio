$(document).ready(function() {
    let slider = document.getElementById("slider");
    let pages_count_element = document.getElementById("pages-count");
    let percent_pages_element = document.getElementById("percent-pages");

    if (slider) {
        slider.oninput = function() {
            let total_pages = pages_count_element.dataset.totalPages;
            pages_count_element.innerHTML = this.value + " pages";
            percent_pages_element.innerHTML = (100*this.value/total_pages).toFixed(1) + " %";
        };

        pages_count_element.innerHTML = slider.value + " pages";
    }
});

function mytoggle(id) {
    var x = document.getElementById(id);
    if (x.style.display == "none") {
        x.style.display = "";
    } else {
        x.style.display = "none";
    }
};

function toggle_slider() {
    let sliderBlock = document.getElementById("slider-block");
    if (sliderBlock.style.display == "none") {
        let slider = document.getElementById("slider");
        let pages_count_element = document.getElementById("pages-count");
        let percent_pages_element = document.getElementById("percent-pages");
        let current_pages = pages_count_element.dataset.currentPages;
        let total_pages = pages_count_element.dataset.totalPages;
        slider.value = current_pages;
        pages_count_element.innerHTML = slider.value + " pages";
        percent_pages_element.innerHTML = (100*slider.value/total_pages).toFixed(1) + " %";
    }
    mytoggle("slider-block");
    mytoggle("update-button-block");
    mytoggle("save-button-block");
};

async function save_reading_update(reading_id) {
    let slider = document.getElementById("slider");
    let new_pages = slider.value
    const payload = 'new_pages=' + new_pages
    let response = await fetch("/books/mark_reading_pages/" + reading_id,
        {
            method: "POST",
            headers: {
                "Content-Type": 'application/x-www-form-urlencoded',
            },
            body: payload,
        }
    );
    response = await response;
    console.log(response.status);
    if (response.status == 200) {
        location.reload();
    }
};