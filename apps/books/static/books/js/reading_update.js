function update_slider(reading_id) {
    let slider = document.getElementById("slider-element-"+reading_id);
    let pages_count_element = document.getElementById("pages-count-"+reading_id);
    let pages_percent_element = document.getElementById("pages-percent-"+reading_id);

    let total_pages = pages_count_element.dataset.totalPages;
    pages_count_element.innerHTML = slider.value + " / " + total_pages + " pages";
    pages_percent_element.innerHTML = (100*slider.value/total_pages).toFixed(1) + " %";
};

function mytoggle(id) {
    var x = document.getElementById(id);
    if (x.style.display == "none") {
        x.style.display = "";
    } else {
        x.style.display = "none";
    }
};

function toggle_slider(reading_id) {
    let slider_block_id = "slider-block-" + reading_id
    let slider_id = "slider-element-" + reading_id
    let pages_count_id = "pages-count-" + reading_id
    let pages_percent_id = "pages-percent-" + reading_id
    let update_button_block_id = "update-button-block-" + reading_id
    let save_button_block_id = "save-button-block-" + reading_id

    let sliderBlock = document.getElementById(slider_block_id);

    if (sliderBlock.style.display == "none") {
        let slider = document.getElementById(slider_id);
        let pages_count_element = document.getElementById(pages_count_id);
        let percent_pages_element = document.getElementById(pages_percent_id);
        let current_pages = pages_count_element.dataset.currentPages;
        let total_pages = pages_count_element.dataset.totalPages;
        slider.value = current_pages;
        pages_count_element.innerHTML = slider.value + " / " + total_pages + " pages";
        percent_pages_element.innerHTML = (100*slider.value/total_pages).toFixed(1) + " %";
    }
    mytoggle(slider_block_id);
    mytoggle(update_button_block_id);
    mytoggle(save_button_block_id);
};

async function save_reading_update(reading_id) {
    let slider = document.getElementById("slider-element-"+reading_id);
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

function add_pages_to_slider(reading_id, pages) {
    let slider = document.getElementById("slider-element-"+reading_id);

    slider.value = parseInt(slider.value) + parseInt(pages);
    update_slider(reading_id);
};