$('.header__nav').closable({
    objectToClose: 'header__nav',
    buttonToClose: 'header__menu--button',
    excludeArea: 'header__auth--item'
});

$('.js-menu').on('click', function() {
    $(this).toggleClass('is-active')
    $('.header__nav').toggleClass('is-active')
})