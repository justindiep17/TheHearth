function setFeaturedCardHeight() {
    var featured_cards = document.getElementsByClassName("carousel-item");
    var len = featured_cards.length;
    for (let i = 0; i < len; i++) {
        featured_cards[i].style.height = 'auto';
    }
    var max_height = 0;
    // Determine The Max Height of Any FeaturedPostCard
    for (let i = 0; i < len; i++) {
        if (featured_cards[i].offsetHeight > max_height) {
            max_height = featured_cards[i].offsetHeight
        }
    }
    // Adjust The Height of Each FeaturedPostCard to Be Equal To max_height
    for (let i = 0; i < len; i++) {
        featured_cards[i].style.height = max_height+'px';
    }
    console.log("window resized justin")
}

function setFeaturedImgHeight() {
    var featured_imgs = document.getElementsByClassName("featured-img");
    var len = featured_imgs.length;
    for (let i = 0; i < len; i++) {
        featured_imgs[i].style.height = 'auto';
    }
    var max_height = 0;
    // Determine The Max Height of Any FeaturedPostCard
    for (let i = 0; i < len; i++) {
        if (featured_imgs[i].offsetHeight > max_height) {
            max_height = featured_imgs[i].offsetHeight
        }
    }
    // Adjust The Height of Each FeaturedPostCard to Be Equal To max_height
    for (let i = 0; i < len; i++) {
        featured_imgs[i].style.height = max_height+'px';
    }
}

function setCardImgHeight() {
    var card_imgs = document.getElementsByClassName("card-img-top");
    var len = card_imgs.length;
    for (let i = 0; i < len; i++) {
        card_imgs[i].style.height = 'auto';
    }
    var max_height = 0;
    // Determine The Max Height of Any FeaturedPostCard
    for (let i = 0; i < len; i++) {
        if (card_imgs[i].offsetHeight > max_height) {
            max_height = card_imgs[i].offsetHeight
        }
    }
    // Adjust The Height of Each FeaturedPostCard to Be Equal To max_height
    for (let i = 0; i < len; i++) {
        card_imgs[i].style.height = max_height+'px';
    }
}



function wrapper() {
    setFeaturedCardHeight();
    setCardImgHeight();
    setFeaturedImgHeight();
}

window.onload = wrapper;
window.addEventListener('resize', wrapper);
