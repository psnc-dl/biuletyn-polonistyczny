var iCheck = {
    init: function() {
        $('input:not([id*="__prefix__"])').each(function() {
            $(this).iCheck({
                checkboxClass: 'icheckbox__main',
                radioClass: 'iradio__main',
            })
        })
    }
}

iCheck.init()