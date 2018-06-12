$('.account__photo--changeuserpic').closable()

$('.js-change-user-photo').on('click', function() {
    $(this).parent().toggleClass('is-active')
})