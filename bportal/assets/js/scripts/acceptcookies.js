(function($) {
    $.fn.cookiepolicy = function(options) {
        new jQuery.cookiepolicy($(this), options);
        return this;
    };

    $.cookiepolicy = function(options) {
        options = $.extend({
            cookie: 'cookiepolicyinfo',
        }, options || {});

        if(Cookies.get(options.cookie) != 'true') {
            $('.js-cookies').fadeIn(100);

            $('.js-cookies-accept').on('click', function(e) {
                e.preventDefault();
                Cookies.set(options.cookie, true)
                $(this).parents('.js-cookies').fadeOut(100);
            });
        }
    };
})(jQuery);

$.cookiepolicy();


