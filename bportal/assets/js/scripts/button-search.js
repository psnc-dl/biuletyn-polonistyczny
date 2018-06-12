$('.header__search').closable({
    objectToClose: 'header__search--box-form',
    buttonToClose: 'header__search--button',
});

$('.js-search').on('click', function() {
    $('.header__search--box-form').toggleClass('is-active')
})