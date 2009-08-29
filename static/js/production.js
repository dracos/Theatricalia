function edit() {
}

$(function() {
    // Make select multiples nicer
    //$("select[multiple]").attr('title', 'Select where it was performed...');
    //$("select[multiple]").asmSelect({
    //    listType: 'ul',
    //    //highlight: true,
    //    animate: true
    //});

    $('#production_edit_inline').change(function(){
        $('#edit-form-submit').removeAttr('disabled');
    });

    table = $('table.parts');
    $('#edit-link a').click(function(){
        table.addClass('order');
        //table.disableSelection();
        table.tableDnD({
            onDragClass: 'parts-drag-highlight',
            onDrop: function(){
                $('#edit-form-submit').removeAttr('disabled');
            }
        });
        table.find('a').click(function() { return false; });
        $('#production-stuff').hide();
        $('#production_meta').slideUp(900);
        $('#production_edit_inline_basic').show();
        $('#edit-form').slideDown(600);
        return false;
    });
    $('form#production_edit_inline').submit(function(){
        table.removeClass('order');
        $('#edit-form-submit').attr('disabled', 'disabled');
        table.tableDnDDisable();
        table.find('a').unbind('click');
        $('#edit-form').slideUp('slow');
        $('#production_edit_inline_basic').hide();
        $('#production_meta').slideDown('slow');
        $('#production-stuff').show();
        return false;
    });
});
