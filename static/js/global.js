jQuery(window).load(function() {
    // Crazyweird fix lets us style abbr using CSS in IE - do NOT run onDomReady, must be onload
    document.createElement('abbr');
});

$.fn.wait = function(time, type) {
    time = time || 1000;
    type = type || 'fx';
    return this.queue(type, function() {
        var self = this;
        setTimeout(function() {
            $(self).dequeue();
        }, time);
    });
};

var start_tab;
$(function() {
    $('#messages').wait(3000).slideUp('slow');

    var edit_link = $('#edit-link a');
    if (edit_link.length) {
        var href = edit_link.attr('href');
        edit_link.attr('href', href.substr(0, href.indexOf('?')));
    }

    $('#search_tabs').tabs({
        selected: start_tab,
        select: function(e, ui) {
            window.location.hash = ui.tab.hash;
        }
    });
    if ($('#search_tabs').length && window.location.hash) {
        window.scrollTo(0, 0);
    }

    $('form#edit .place:last').after(
        $('<p>If this production performed at another place, <a href="">add another place</a>.</p>').click(function(){
            var last_form = $('form#edit .place:last');
            var newRow = last_form.clone().insertAfter(last_form);
            var total = $('#id_place-TOTAL_FORMS').val();
            var old_id = '-' + (total-1) + '-';
            var new_id = '-' + total + '-';
            newRow.find(':input').each(function(){
                var name = $(this).attr('name').replace(old_id, new_id);
                var id = 'id_' + name;
                $(this).attr({'name': name, 'id': id}).val('');
            });
            newRow.find('label').each(function(){
                var newFor = $(this).attr('for').replace(old_id, new_id);
                $(this).attr('for', newFor);
            });
            total++;
            $('#id_place-TOTAL_FORMS').val(total);

            autocomplete_add({
                lookup: "#id_place-" + (total-1) + "-place_0",
                id: '#id_place-' + (total-1) + '-place_1',
                search_fields: 'name',
                app_label: 'places',
                model_name: 'place'
            });

            return false;
        })
    );
});

/* Map code */
var map, tinyIcon;
$(function() {
    if (!document.getElementById('map')) return;

    $('#map').show();
    $('#map-nojs').hide();

    var cloudmade = new CM.Tiles.CloudMade.Web({key: '28fad93380975f22a60c0f855ce380ca', styleId:5950});
    map = new CM.Map('map', cloudmade);
    map.setCenter(new CM.LatLng(53.5, -1.7), 5);
    map.enableScrollWheelZoom();
    map.enableDoubleClickZoom();
    map.enableShiftDragZoom();
    var topRight = new CM.ControlPosition(CM.TOP_RIGHT, new CM.Size(2, 2));
    map.addControl(new CM.LargeMapControl(), topRight);
    map.addControl(new CM.ScaleControl());

    tinyIcon = new CM.Icon();
    tinyIcon.image = '/static/i/pin-red.png';
    tinyIcon.shadow = '/static/i/pin-shadow.png';
    tinyIcon.iconSize = new CM.Size(12, 20);
    tinyIcon.shadowSize = new CM.Size(22, 20);
    tinyIcon.iconAnchor = new CM.Point(6, 20);
    tinyIcon.infoWindowAnchor = new CM.Point(5, 1);

    /* Unless we're on an editing page, we're done */
    if (!document.getElementById('id_latitude')) return;
    
    $('#form_latlon').hide();
    var lat = $('#id_latitude')[0].value || 0;
    var lon = $('#id_longitude')[0].value || 0;
    var opts = { icon: tinyIcon, draggable: true };
    marker = new CM.Marker(new CM.LatLng(lat, lon), opts);
    map.addOverlay(marker);
    if (!lat && !lon) {
        marker.hide();
        $('#map').before('<p style="margin-top:0">Please locate this theatre by positioning the map, then drag the pin from the corner to the right location. You can reposition the pin.</p>');
    } else {
        $('#map').before('<p style="margin-top:0">Please locate the theatre by dragging the pin.</p>');
        map.setCenter(new CM.LatLng(lat, lon), 13);
    }
    $('#map').after('<p style="margin-top:0"><small>You can zoom by using the controls, double-clicking, using your scroll wheel, or shift-dragging an area.</small></p>');

    var pinControl = function(){};
    pinControl.prototype = {
        initialize: function(map, position) {
            var control = document.createElement('div');
            control.style.background = 'white';
            control.style.padding = '5px';
            control.style.borderBottom = '1px solid #666';
            control.style.borderRight = '1px solid #666';
            var pin = document.createElement('img');
            pin.id = 'draggablePin';
            pin.src = '/static/i/pin-red.png';
            $(pin).draggable({ revert:'invalid', helper:'clone', cursor:'crosshair', cursorAt:{ bottom:0 } });
            control.appendChild(pin);
            map.getContainer().appendChild(control);
            return control;
        },
        getDefaultPosition: function() {
            return new CM.ControlPosition(CM.TOP_LEFT, new CM.Size(0,0));
        }
    };
    map.addControl(new pinControl());

    $('#map').droppable({
        drop: function(event, ui) {
            var latlng = map.fromContainerPixelToLatLng(new CM.Point(ui.position.left + 6, ui.position.top + 20));
            marker.setLatLng(latlng);
            marker.show();
            updateInputs(latlng);
        }
    });

    $('#id_town').change(function(){
        $.getJSON('http://ws.geonames.org/searchJSON?q=' + $('#id_town').val() + '&maxRows=1&callback=?', function(data) {
            if (data.geonames.length) {
                var lat = data.geonames[0].lat;
                var lng = data.geonames[0].lng;
                map.setCenter(new CM.LatLng(lat, lng), 13);
            }
        });
    });

    function updateInputs(point) {
        $('#id_latitude').val(point.lat());
        $('#id_longitude').val(point.lng());
        if ($('#id_town').val()) return;
        // If no town, pre-populate with one from geonames
        $.getJSON('http://ws.geonames.org/findNearbyPlaceNameJSON?lat=' + point.lat() + '&lng=' + point.lng() + '&style=full&radius=5&callback=?', function(data) {
            var pop_max = 0;
            var pop_item;
            $.each(data.geonames, function(i, item) {
                if (item.population && item.population > pop_max) {
                    pop_max = item.population;
                    pop_item = item;
                }
            });
            if (pop_item) {
                $('#id_town').val(pop_item.name);
            } else {
                $('#id_town').val(data.geonames[0].name);
            }
        });
    }

    CM.Event.addListener(marker, "dragend", function() {
        var point = this.getLatLng();
        updateInputs(point);
    });
    //CM.Event.addListener(map, 'click', function(point) {
    //    marker.setLatLng(point);
    //    marker.show();
    //    updateInputs(point);
    //});
});


/* Autocomplete stuff */

function autocomplete_add(params) {
    $(params.lookup).autocomplete("/ajax/autocomplete", {
        extraParams: {
            search_fields: params.search_fields,
            app_label: params.app_label,
            model_name: params.model_name
        },
        matchContains:1,
        max:20,
        selectFirst:0
    }).result(function(event, data, formatted) {
        if (data) {
            $(params.id).val( data[1] );
        }
    }).blur(function(){
        $(params.lookup).search(function (result) {
            if (result && result.data) {
                $(params.id).val( result.data[1] );
            } else {
                $(params.id).val( "" );
            }
        });
    });
}

