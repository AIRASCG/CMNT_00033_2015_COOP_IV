$.ctrl = function(key, callback, args) {
    $(document).keydown(function(e) {
        if(!args) args=[]; // IE barks when args is null
        if((e.keyCode == key.charCodeAt(0) || e.keyCode == key) && e.altKey && e.shiftKey) {
            callback.apply(this, args);
            return false;
        }
    });
};

//Previous object
$.ctrl('38', function() {
    $('.oe_i[data-pager-action="previous"]').each(function() {
        if($(this).parents('div:hidden').length == 0){
            $(this).trigger('click');
        }
    });
});

//Next object
$.ctrl('40', function() {
    $('.oe_i[data-pager-action="next"]').each(function() {
        if($(this).parents('div:hidden').length == 0){
            $(this).trigger('click');
        }
    });
});

//SaveAndNew One2Many Form
$.ctrl('13', function() {
        $('.oe_abstractformpopup-form-save-new').each(function() {
                if($(this).parents('div:hidden').length == 0){
                        $(this).trigger('click');
                }
        });
});
