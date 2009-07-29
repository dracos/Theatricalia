function edit() {
}

$(function() {
    // Make select multiples nicer
    $("select[multiple]").attr('title', 'Select any location this production was performed...');
    $("select[multiple]").asmSelect({
        listType: 'ul',
        //highlight: true,
        animate: true
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
        $('#edit-link').hide();
        $('#production_meta').slideUp(1000);
        $('#production_edit_inline_basic').fadeIn(1000);
        $('#edit-form').slideDown('slow');
        return false;
    });
    $('form#production_edit_inline').submit(function(){
        table.removeClass('order');
        $('#edit-form-submit').attr('disabled', 'disabled');
        table.tableDnDDisable();
        table.find('a').unbind('click');
        $('#edit-form').slideUp('slow');
        $('#production_edit_inline_basic').hide();
        $('#production_meta').show();
        $('#edit-link').show();
        return false;
    });
});
