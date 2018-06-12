$('.list__item--edit').on('click', function(event){
    event.stopPropagation();
    var url = $(this).attr('data-link')
    window.open(url, '_parent').location;
    return false;
});