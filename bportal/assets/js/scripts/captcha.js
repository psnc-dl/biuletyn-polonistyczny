$(function() {
    $('.contact__form--captcha-refresh').on('click', function(){
        var $form = $(this).parents('form');
        var url = location.protocol + "//" + window.location.hostname + ":" + location.port + "/" + baseURL + "captcha/refresh/";
        $.getJSON(url, {}, function(json) {
            $form.find('input[name="captcha_0"]').val(json.key);
            $form.find('.contact__form--captcha-img').attr('src', json.image_url);
        });

        return false;
    });

    $('.contact__form--button-submit').on('click', function(){
        $(this).parents('form').find('.contact__form--captcha-refresh').click()
        $(this).parents('form').find('.contact__form--input').val('')
    });
});