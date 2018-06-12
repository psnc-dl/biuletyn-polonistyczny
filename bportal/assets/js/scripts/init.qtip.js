var qTip = {
    init: function() {
        $('[title]:not([id*="__prefix__"])').each(function() {
            $(this).qtip({
                position: {
                    my: 'top left',
                    at: 'bottom right',
                    viewport: $(window)
                }
            });
        })
    }
}

qTip.init()


