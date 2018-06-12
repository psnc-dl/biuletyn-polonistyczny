$('.paginate__input').on('keyup mouseup', function() {
    var max = parseInt($(this).attr('max'))

    if (parseInt($(this).val()) > max) {
        $(this).val(max)
    }
})

$('.paginate__input').on('change', function() {
    var url = new URL(window.location.href);
    var page = $(this).val()

    url.searchParams.set("page", page);

    location.replace(url.href)
})