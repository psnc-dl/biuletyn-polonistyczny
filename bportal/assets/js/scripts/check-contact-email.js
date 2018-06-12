var checkContactEmail = {
    init: function() {
        var elem = $('.js-check-contact-email')
        var text = elem.text()

        if (this._checkString(text)) {
            elem.replaceWith(function() {
                return '<a href="mailto: ' + text + '" class="' + elem.attr('data-link-class') + '" title="' + elem.attr('data-link-title') + '">' + text + '</a>';
            });
        }
    },
    _checkString: function(string) {
        var re = /(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))/;
        return re.test(string);
    }
}

checkContactEmail.init();



