$.fn.editable = function(url, options) {
    // Options
    options = arrayMerge({
            "url": url,
            "paramName": "q",
            "callback": null,
            "saving": "saving ...",
            "type": "text",
            "submitButton": 0,
            "delayOnBlur": 0,
            "extraParams": {},
            "editClass": null
            }, options);
    // Set up
    this.click(function(e) {
            if (this.editing) return;
            if (!this.editable) this.editable = function() {
            var me = this;
            me.editing = true;
            me.orgHTML = $(me).html();
            me.innerHTML = "";
            if (options.editClass) $(me).addClass(options.editClass);
            var f = document.createElement("form");
            var i = createInputElement(me.orgHTML);
            var t = 0;
            f.appendChild(i);
            if (options.submitButton) {
            var b = document.createElement("input");
            b.type = "submit";
            b.value = "Finish";
            f.appendChild(b);
            }
            me.appendChild(f);
            i.focus();
            $(i).blur(
                options.delayOnBlur ? function() { t = setTimeout(reset, options.delayOnBlur) } : reset
                )
                .keydown(function(e) {
                        if (e.keyCode == 27) { // ESC
                        e.preventDefault;
                        reset
                        }
                        });
            $(f).submit(function(e) {
                    if (t) clearTimeout(t);
                    e.preventDefault();
                    var p = {};
                    p[i.name] = $(i).val();
                    $(me).html(options.saving).load(options.url, arrayMerge(options.extraParams, p), function() {
                        // Remove script tags
                        me.innerHTML = me.innerHTML.replace(/<\s*script\s*.*>.*<\/\s*script\s*.*>/gi, "");
                        // Callback if necessary
                        if (options.callback) options.callback(me); 
                        // Release
                        me.editing = false;                     
                        });
                    });
            function reset() {
                me.innerHTML = me.orgHTML;
                if (options.editClass) $(me).removeClass(options.editClass);
                me.editing = false;                 
            }
            };
            this.editable();
    })
    ;
    // Don't break the chain
    return this;
    // Helper functions
    function arrayMerge(a, b) {
        if (a) {
            if (b) for(var i in b) a[i] = b[i];
            return a;
        } else {
            return b;       
        }
    };
    function createInputElement(v) {
        if (options.type == "textarea") {
            var i = document.createElement("textarea");
            options.submitButton = true;
            options.delayOnBlur = 100; // delay onBlur so we can click the button
        } else {
            var i = document.createElement("input");
            i.type = "text";
        }
        $(i).val(v);
        i.name = options.paramName;
        return i;
    }
};

function edit() {
    $(this).editable('/url', {type:'textarea'});
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
        $('.editpossible').addClass('editable').attr('title', 'Click to edit').click(edit);
        // $('table.parts').sortable({ containment: 'parent', cursor: 'move', items: 'tr' });
        //table.disableSelection();
        table.tableDnD({
            onDragClass: 'parts-drag-highlight',
            onDrop: function(){
                $('#edit-form-submit').removeAttr('disabled');
            }
        });
        table.find('a').click(function() { return false; });
        $(this).parent().hide();
        $('#edit-form').show();
        return false;
    });
    $('#edit-form form').submit(function(){
        table.removeClass('order');
        $('#edit-form-submit').attr('disabled', 'disabled');
        $('.editpossible').removeClass('editable').attr('title', '').unbind('click');
        //table.sortable('destroy');
        table.tableDnDDisable();
        table.find('a').unbind('click');
        $(this).parent().hide();
        $('#edit-link').show();
        return false;
    });
});
