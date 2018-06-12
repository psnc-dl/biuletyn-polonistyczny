$('.header__nav--item').closable()

$('.js-menu-dropdown').on('focus', function() {
    $(this).parent().siblings().removeClass('is-active')
    $(this).parent().toggleClass('is-active')
})