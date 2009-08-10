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
});

var map, tinyIcon;
$(function() {
    if (GBrowserIsCompatible() && document.getElementById('map')) {
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
            var lat = $('#id_latitude')[0].value || 0;
            var lon = $('#id_longitude')[0].value || 0;
            var opts = { icon: tinyIcon, draggable: true };
            if (!lat && !lon) {
                opts['hide'] = true;
            } else {
                map.setCenter(new GLatLng(lat, lon), 13);
            }
            marker = new GMarker(new GLatLng(lat, lon), opts);
            map.addOverlay(marker);
            GEvent.addListener(marker, "dragend", function() {
                var point = this.getLatLng();
                $('#id_latitude')[0].value = point.lat();
                $('#id_longitude')[0].value = point.lng();
            });
            GEvent.addListener(map, 'click', function(overlay, point) {
                if (point) {
                    marker.setLatLng(point);
                    marker.show();
                    $('#id_latitude')[0].value = point.lat();
                    $('#id_longitude')[0].value = point.lng();
                }
            });
        }
    }
});


