$(document).ready(function(){
    if (window.location.hash && $(window.location.hash).length > 0) {
        scrollTop.init(window.location.hash)
    }

    $("a").on('click', function(event) {
        if (this.hash !== "" && !this.hash.startsWith("#/profile/scientist?")) {
            event.preventDefault();
            scrollTop.init(this.hash)
        }
    });
});

var scrollTop = {
    init: function(locate) {
        $('html, body').animate({
            scrollTop: $(locate).offset().top - 70
        }, 800);
        window.location.hash = locate
    }
};