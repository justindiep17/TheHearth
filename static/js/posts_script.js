function setPostPreviewCardsHeight() {
    var post_lst = document.getElementsByClassName("preview-card");
    var len = post_lst.length
    for (let i = 0; i < len; i++) {
        post_lst[i].style.height = 'auto';
    }
    var max_height = 0
    // Determine The Max Height of Any PostPreviewCard
    for (let i = 0; i < len; i++) {
        if (post_lst[i].offsetHeight > max_height) {
            max_height = post_lst[i].offsetHeight
        }
    }
    // Adjust The Height of Each PostPreviewCard to Be Equal To max_height
    for (let i = 0; i < len; i++) {
        post_lst[i].style.height = max_height+'px';
    }
    console.log("window resized justin")
}

window.onload = setPostPreviewCardsHeight

window.addEventListener('resize', setPostPreviewCardsHeight);