//-------------------------------------------------------------------------------------- //
//INLINES Adding new inline
//-------------------------------------------------------------------------------------- //

$.fn.hasAttr = function(name) {
    return this.attr(name) !== undefined;
};

$(document).on('click', '.js-add-inline', function (e) {
    e.preventDefault();
    var Element = $(this).parent().siblings('[class*="_empty"]');
    var newElement = Element.clone(false);

    var col = $(this).parent().parent().data('prefix');

    var total_field = $(this).parent().parent().siblings('#id_'+ col +'-TOTAL_FORMS');
    var maxNum_field = $(this).parent().parent().siblings('#id_'+ col +'-MAX_NUM_FORMS');

    var total = parseInt(total_field.val());
    var maxNum = parseInt(maxNum_field.val());

    newElement.each(function() {
        var newClass = $(this).attr('class').replace('_empty', '');
        $(this).attr('class', newClass);
    });

    newElement.find("*").each(function() {
        if ($(this).hasAttr('id')) {
            var newId = $(this).attr('id').replace('-__prefix__-','-' + (total) + '-');
            $(this).attr('id', newId);
        }

        if ($(this).hasAttr('for')) {
            var newFor = $(this).attr('for').replace('-__prefix__-','-' + (total) + '-');
            $(this).attr('for', newFor);
        }

        if ($(this).hasAttr('name')) {
            var newName = $(this).attr('name').replace('-__prefix__-','-' + (total) + '-');
            $(this).attr('name', newName);
        }
    });

    total++;
    total_field.val(total);

    Element.before(newElement);

    iCheck.init()
    customFile.init()
    qTip.init()
});
//-------------------------------------------------------------------------------------- //
//END of INLINES Adding new inline
//-------------------------------------------------------------------------------------- //
//-------------------------------------------------------------------------------------- //
//INLINES Delete inline
//-------------------------------------------------------------------------------------- //

$(document).on('click', '.js-remove-inline', function () {
    var col = $(this).parent().parent().data('prefix');

    var total_field = $(this).parent().parent().siblings('#id_'+ col +'-TOTAL_FORMS');
    var initial_field = $(this).parent().parent().siblings('#id_'+ col +'-INITIAL_FORMS');

    var total = parseInt(total_field.val());
    var initial = parseInt(initial_field.val());
    console.log(total)
    console.log(initial)

    //TODO: why we don't use total?
    //var howmany = parseInt($(this).parent().children('div:not([class*="_empty"])').length);
    var howmany = total - 1

    if ( howmany>initial )
    {
        $(this).parent().siblings('ul:last').prev().remove();
        total_field.val(howmany);
    }
});
//-------------------------------------------------------------------------------------- //
//END of INLINES Delete inline
//-------------------------------------------------------------------------------------- //

$('.autocomplete-add-another').find('img').remove()
$('.autocomplete-add-another').html('<i class="bp-icon-file_plus page__form--icon-add"></i>')