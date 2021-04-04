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
    //$('#messages').wait(3000).slideUp('slow');

    $('#navigation a').hover(function(){
        $('#navigation a').not(this).addClass('greyed');
    }, function(){
        $('#navigation a').not(this).removeClass('greyed');
    });

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

    /* fancybox
       Rewrite all Flickr photos to go to their pictures directly,
       deal with the special big photo at the top,
       and then set up fancybox galleries for all the photos.
     */
    $('a[href^="https://www.flickr.com"]').each(function(){
        var l = $(this);
        var pic = l.find('img').attr('src');
        if (pic) {
            pic = pic.replace('_s.', '_z.');
            l.data('orighref', l.attr('href'));
            l.attr('href', pic);
        }
    });
    $('#photograph-feature a').click(function(){
        $('a[rel=gallery][href^="' + $(this).attr('href') + '"]').click();
        return false;
    });
    $('a[rel=gallery]').fancybox({
        'overlayOpacity': '0.8',
        'overlayColor': '#000000',
        'cyclic': 'true',
        'opacity': 'true',
        'transitionIn': 'elastic',
        'transitionOut': 'elastic',
        'titlePosition': 'over',
        'titleFormat': function(title, currentArray, currentIndex, currentOpts) {
            if (currentOpts.href.substring(0, 7) == 'http://') {
                var orig = $(currentArray[currentIndex]).data('orighref');
                title += ' <a href="' + orig + '">View on Flickr</a>';
            }
            var image_idx = '';
            if (currentArray.length > 1) {
                if (title.length) title = ' &nbsp; ' + title;
                image_idx = 'Image ' + (currentIndex + 1) + ' / ' + currentArray.length;
            }
            return '<span id="fancybox-title-over">' + image_idx + title + '</span>';
        }
    });

    // Add another place when editing production
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

    $('form#edit .name:last').after(
        $('<p>If this place had another name, <a href="">add another name</a>.</p>').click(function(){
            var last_form = $('form#edit .name:last');
            var newRow = last_form.clone().insertAfter(last_form);
            var total = $('#id_name-TOTAL_FORMS').val();
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
            $('#id_name-TOTAL_FORMS').val(total);

            return false;
        })
    );

    $('form#edit .company:last').after(
        $('<p style="margin-left:8.5em"><small><a href="">Add another company</a></small></p>').click(function(){
            var last_form = $('form#edit .company:last');
            var newRow = last_form.clone().insertAfter(last_form);
            var total = $('#id_company-TOTAL_FORMS').val();
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
            $('#id_company-TOTAL_FORMS').val(total);

            autocomplete_add({
                lookup: "#id_company-" + (total-1) + "-productioncompany_0",
                id: '#id_company-' + (total-1) + '-productioncompany_1',
                search_fields: 'name',
                app_label: 'productions',
                model_name: 'productioncompany'
            });

            return false;
        })
    );

    // Add another author when editing play
    $('form#edit .author:last').after(
        $('<p style="margin-left:8.5em"><small><a href="">Add another author</a></small></p>').click(function(){
            var last_form = $('form#edit .author:last');
            var newRow = last_form.clone().insertAfter(last_form);
            var total = $('#id_form-TOTAL_FORMS').val();
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
            $('#id_form-TOTAL_FORMS').val(total);

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

    //var cloudmade = new CM.Tiles.CloudMade.Web({key: '28fad93380975f22a60c0f855ce380ca', styleId:5950});
    var os_map = new CM.Tiles.OpenStreetMap.Mapnik({
        title: 'OS OpenMap Local (GB)',
        tileUrlTemplate: 'https://#{subdomain}.os.openstreetmap.org/layer/gb_os_om_local_2020_04/#{zoom}/#{x}/#{y}.png',
        copyright: 'Ordnance Survey data &copy; Crown<br>copyright and database right 2020.',
        minZoomLevel: 8,
        maxZoomLevel: 18
    });
    var cloudmade = new CM.Tiles.OpenStreetMap.Mapnik({
        tileUrlTemplate: 'https://#{subdomain}.tile.openstreetmap.org/#{zoom}/#{x}/#{y}.png',
        title: 'OpenStreetMap'
    });
    map = new CM.Map('map', [ cloudmade, os_map ]);
    map.setCenter(new CM.LatLng(53.5, -1.7), 8);
    map.enableScrollWheelZoom();
    map.enableDoubleClickZoom();
    map.enableShiftDragZoom();
    var topRight = new CM.ControlPosition(CM.TOP_RIGHT, new CM.Size(2, 40));
    map.addControl(new CM.LargeMapControl(), topRight);
    map.addControl(new CM.ScaleControl());
    map.addControl(new CM.TileLayerControl());

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
        matchSubset:false,
        max:20,
        multipleSeparator: '|',
        selectFirst:0
    }).result(function(event, data, formatted) {
        if (data) {
            $(params.id).val( data[1] );
        }
    }).blur(function(){
        if (!$(params.lookup).val()) return;
        $(params.lookup).search(function (result) {
            if (result && result.data) {
                // $(params.id).val( result.data[1] );
            } else {
                $(params.id).val( "" );
            }
        });
    });
}

