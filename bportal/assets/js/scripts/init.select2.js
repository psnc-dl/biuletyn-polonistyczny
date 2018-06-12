var Select2 = {
    init: function() {
        $('select.select2:not([id*="__prefix__"])').each(function() {
            $(this).select2({
                minimumResultsForSearch: -1
            })
        })
    }
}



if ($('.select2').length > 0) {
    Select2.init()
}