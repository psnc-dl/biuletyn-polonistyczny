$('.js-sorting').on('change', function() {
    var sortingValue = $(this).val()
    $('#id_o').val(sortingValue)
    $('#id_o').parents('form').submit()
})