$("#send_newsletter").click(function(){
    var $form = $(this).parents('form');
    var url = location.protocol + "//" + window.location.hostname + ":" + location.port + "/" + baseURL + "subscribe/";
    $.getJSON(url, $form.serialize(), function(json) {
        $(".errorlist").remove();
        var obj = $.parseJSON(json);
        for (var key in obj.errors) {
            error = obj.errors[key];
            if (key == 'captcha') {
                $("input#news_id_" + key + "_1").after(error);
            } else {
                $("input#id_" + key).after(error);
            }
        }
        if (obj.ok) {
            document.getElementById("newsletter_subscription").reset();
            $(".newsletterFormWarnings").append("<ul class=successlist><li>"+ obj.ok + "</li></ul>").delay(5000).queue(function(next){
                $(this).fadeOut('fast').remove();
            });
        }
    });
    $('.captcha-refresh').click()
    return false;
});