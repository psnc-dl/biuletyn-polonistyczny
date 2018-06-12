var newsCategory = (function() {
    var hiddenClass = 'page__form--initially-hidden';
    var defaultBoxes = ['new_keywords', 'new_description', 'new_files', 'new_links'];

    var categoryID;
    var initialize = false;

    function init() {
        categoryID = $('select[name="new_category"]').val();
        _showBox(categoryID);
        initialize = true;
    }

    function onChange() {
        $('.page select[name="new_category"]').on('change', function () {
            categoryID = $(this).val();
            _showBox(categoryID);
            _clearBox();
        })
    }

    function _showBox(catID) {
        var catName = _category(catID)
        if ($('.' + hiddenClass + '.' + catName).length > 0) {
            $('.' + hiddenClass).removeClass('is-active');
            $('.' + hiddenClass + '.' + catName).addClass('is-active');
        } else {
            $('.' + hiddenClass).removeClass('is-active');
            if (initialize || !!categoryID) {
                $.each( defaultBoxes, function( i, box ) {
                    $('.' + hiddenClass + '.' + box).addClass('is-active');
                });
            }
        }
    }

    function _clearBox() {
        $('.' + hiddenClass).find('select').each(function(){
            $(this).find('option').attr('selected',false);
            $(this).find('option[value=""]').attr('selected','selected');
            $(this).val( $(this).prop('defaultSelected') ).trigger('change');
        });

        $('.' + hiddenClass).find('textarea, input[type="text"], input[type="file"]').each(function(){
            $(this).val('');
        });

        $('.' + hiddenClass).find('input[type="checkbox"], input[type="radio"]').each(function(){
            $(this).iCheck('uncheck')
        });

        if ($(CKEDITOR.instances).length) {
            for (var key in CKEDITOR.instances) {
                var instance = CKEDITOR.instances[key];
                if ($(instance.element.$)[0].id == 'id_new_description') {
                    instance.setData( '', function() { this.updateElement(); } );
                }
            }
        }
    }

    function _category(catID) {
        switch(parseInt(catID)) {
            case 1:
                return 'new_related_event';
                break;
            case 2:
                return 'new_related_project';
                break;
            case 3:
                return 'new_related_dissertation';
                break;
            case 4:
                return 'new_related_competition';
                break;
            case 5:
                return 'new_related_eduoffer';
                break;
            case 6:
                return 'new_related_scholarship';
                break;
            case 7:
                return 'new_related_joboffer';
                break;
            case 8:
                return 'new_related_article';
                break;
            case 9:
                return 'new_related_journalissue';
                break;
            case 10:
            	return 'new_related_book';
                break;
            default:
                return false;
        }
    }

    return {
        init: init,
        onChange: onChange
    }
})();

if ($('select[name="new_category"]').length) {
    newsCategory.init()
    newsCategory.onChange()
}