var detailsGallery = $('.details__gallery')

detailsGallery.on('initialized.owl.carousel', function (event) {
    $('.details__gallery--slides-page').text('1');
    $('.details__gallery--slides-pages').text(event.item.count);
});

detailsGallery.owlCarousel({
    loop:true,
    nav:true,
    dots: true,
    navText: ['<i class="bp-icon-chevron_long_left"></i>','<i class="bp-icon-chevron_long_right"></i>'],
    items: 1,
    autoHeight:true
});

detailsGallery.on('changed.owl.carousel', function (event) {
    $('.details__gallery--slides-page').text(event.page.index + 1);
    $('.details__gallery--slides-pages').text(event.page.count);
});



