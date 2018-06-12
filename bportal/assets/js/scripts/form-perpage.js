$('.js-perpage').on('change', function() {
    var perpageValue = $(this).val()
    $('#id_perpage').val(perpageValue)
    $('#id_perpage').parents('form').submit()
})