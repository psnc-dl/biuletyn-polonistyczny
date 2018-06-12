$('.header__fontsize').closable()

$('.js-fontsize').on('click focus', function() {
    $(this).parent().toggleClass('is-active')
})

$('[name=fontsize]').on('ifChecked', function(){
    var fontsize = $(this).get(0).value
    $('body').attr('data-fontsize', fontsize)
    Cookies.set('FontSize', fontsize);
});

$(function() {
    var fontsize = Cookies.get('FontSize')

    if (!fontsize) {
        $('#fontsize-normal').prop('checked', true)
    } else {
        $('#fontsize-' + fontsize).prop('checked', true)
        $('body').attr('data-fontsize', fontsize)
    }
    $('input[name="fontsize"]').iCheck('update');
});
