
function toggleNav() {
    let toggleTrigger = document.querySelectorAll(".js-toggle-nav");
    for (let i = 0; i < toggleTrigger.length; i++) {
        toggleTrigger[i].addEventListener("touchstart", function() {
            document.querySelector("html").classList.toggle("has-mobile-nav");
        })
    }
}

document.addEventListener("DOMContentLoaded", function() {
    toggleNav();
})