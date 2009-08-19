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

$(function() {
	$('#messages').wait(3000).slideUp('slow');

	$('.edit_status select').change(function(){
		edit_status = $(this).find('option:selected').val();
		if (edit_status == 'leave') {
			$(this).parents('tr').find('input,select').not('.edit_status select').attr('disabled', 'disabled');
			$(this).parents('tr').removeClass('remove');
		} else if (edit_status == 'change') {
			$(this).parents('tr').find('input,select').not('.edit_status select').removeAttr('disabled');
			$(this).parents('tr').removeClass('remove');
		} else if (edit_status == 'remove') {
			$(this).parents('tr').find('input,select').not('.edit_status select').attr('disabled', 'disabled');
			$(this).parents('tr').addClass('remove');
		}
	}).change();

    $('form#edit .place:last').after(
        $('<a href="">Add another</a>').click(function(){
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
            return false;
        })
    );
});

var map, tinyIcon;
$(function() {
    if (document.getElementById('map') && GBrowserIsCompatible()) {
        $(document).unload(function() { GUnload() });
        map = new GMap2(document.getElementById("map"));
        map.addControl(new GLargeMapControl());
        map.setCenter(new GLatLng(53.5, -1.7), 5);

        tinyIcon = new GIcon();
        tinyIcon.image = '/static/i/pin-red.png';
        tinyIcon.shadow = '/static/i/pin-shadow.png';
        tinyIcon.iconSize = new GSize(12, 20);
        tinyIcon.shadowSize = new GSize(22, 20);
        tinyIcon.iconAnchor = new GPoint(6, 20);
        tinyIcon.infoWindowAnchor = new GPoint(5, 1);

        if (document.getElementById('id_latitude')) {
            $('#form_latlon').hide();
            var lat = $('#id_latitude')[0].value || 0;
            var lon = $('#id_longitude')[0].value || 0;
            var opts = { icon: tinyIcon, draggable: true };
            if (!lat && !lon) {
                $('#map').before('<p style="margin-top:0">Please locate this theatre by clicking, then dragging the pin to adjust.</p>');
                opts['hide'] = true;
            } else {
                $('#map').before('<p style="margin-top:0">Please locate the theatre by dragging the pin.</p>');
                map.setCenter(new GLatLng(lat, lon), 13);
            }
            marker = new GMarker(new GLatLng(lat, lon), opts);
            map.addOverlay(marker);

            $('#id_town').change(function(){
                $.getJSON('http://ws.geonames.org/searchJSON?q=' + $('#id_town').val() + '&maxRows=1&callback=?', function(data) {
                    if (data.geonames) {
                        var lat = data.geonames[0].lat;
                        var lng = data.geonames[0].lng;
                        map.setCenter(new GLatLng(lat, lng), 13);
                    }
                });
            });

            function updateInputs(point) {
                $('#id_latitude')[0].value = point.lat();
                $('#id_longitude')[0].value = point.lng();
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

            GEvent.addListener(marker, "dragend", function() {
                var point = this.getLatLng();
                updateInputs(point);
            });
            GEvent.addListener(map, 'click', function(overlay, point) {
                if (point && marker.isHidden()) {
                    marker.setLatLng(point);
                    marker.show();
                    updateInputs(point);
                }
            });
        }
    }
});


