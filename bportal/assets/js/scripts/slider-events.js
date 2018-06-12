var eventsSlider = $('.events__slider');

eventsSlider.on('initialized.owl.carousel', function() {
    $('.events .owl-item').each(function(){
        $(this).find('.events__text--title').truncateTextTwo()
        $(this).find('.events__text--institution').truncateTextNote()
        $(this).find('.events__text--excerpt').truncateTextThree()
    })
});

eventsSlider.owlCarousel({
    loop:true,
    nav:true,
    dots: true,
    navText: ['<i class="bp-icon-chevron_long_left"></i>','<i class="bp-icon-chevron_long_right"></i>'],
    items:1,
    autoHeight:false,
    autoplay:true,
    autoplayTimeout:10000,
    autoplayHoverPause:true
});
