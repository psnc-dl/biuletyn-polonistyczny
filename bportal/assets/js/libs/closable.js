$.fn.extend({
    closable: function(options) {
        var defaults = {
            activeClass: 'is-active',
            escKeyCode: 27,
            objectToClose: false,
            buttonToClose: false,
            excludeArea: false
        };

        var params = $.extend(defaults, options);

        return this.each(function() {
            var obj = $(this);

            $(document).on('click keyup', function (event) {
                event.stopPropagation();

                if ( params.objectToClose && params.buttonToClose ) {
                    if ( $('.' + params.objectToClose).hasClass(params.activeClass) && (event.target.classList[0] !=  params.objectToClose && $(event.target).parents('.' + params.objectToClose).length == 0 && event.target.classList[0] !=  params.buttonToClose && $(event.target).parents('.' + params.buttonToClose).length == 0 ) || $(event.target).parents('.' + params.excludeArea).length > 0 || event.keyCode == params.escKeyCode)
                    {
                        $('.' + params.buttonToClose).removeClass(params.activeClass)
                        $('.' + params.objectToClose).removeClass(params.activeClass)
                    }
                } else {
                    if ($(obj).hasClass(params.activeClass) && (($(event.target).parents('.' + obj[0].classList[0]).length == 0) || event.keyCode == params.escKeyCode)) {
                        $(obj).removeClass(params.activeClass)
                    }
                }
            });


        });

    }
});