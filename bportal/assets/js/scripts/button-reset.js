$('button[type=reset]').on('click', function() {
    $(this).parents('form').find('input:not([type=checkbox])').each(function(){
        $(this).attr('value', '');
    });

    $(this).parents('form').find('input[type=checkbox]').each(function(){
        $(this).iCheck('uncheck');
        $(this).attr('checked', false);
    });

    $(this).parents('form').find('select').each(function(){
        $(this).find('option').attr('selected',false);
        $(this).find('option[value=""]').attr('selected','selected');
        $(this).val( $(this).prop('defaultSelected') ).trigger('change');
    });
});