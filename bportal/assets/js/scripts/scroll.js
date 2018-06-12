$(document).scroll(function() {
    var scrolltop = $(this).scrollTop();
    var offsettop = 400

    if (scrolltop > offsettop) {
        $('header').addClass('is-fixed')
    } else {
        $('header').removeClass('is-fixed')
    }
});