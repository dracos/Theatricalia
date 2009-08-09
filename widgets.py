from datetime import date
from django.utils import dateformat
from django.forms import widgets
from django.utils.safestring import mark_safe

class PrettyDateInput(widgets.Input):
    input_type = 'text'

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        elif isinstance(value, date):
            value = dateformat.format(value, "jS F Y")
        return super(PrettyDateInput, self).render(name, value, attrs)

class LocationWidget(widgets.Widget):
    def __init__(self, *args, **kw):
        super(LocationWidget, self).__init__(*args, **kw)

    def render(self, name, value, *args, **kwargs):
        js = '''
<input type="hidden" name="%(name)s" id="id_%(name)s" value="">
<script type="text/javascript">
    var %(name)s_marker ;
    $(document).ready(function () {
        if (GBrowserIsCompatible()) {
            var map = new GMap2(document.getElementById("map_%(name)s"));
            map.setCenter(new GLatLng(4.735543142197098,-74.0822696685791), 13);
            %(name)s_marker = new GMarker(new GLatLng(4.735543142197098,-74.0822696685791), {draggable: true});
            map.addOverlay(%(name)s_marker);
            map.addControl(new GLargeMapControl());
            $('#id_latitude')[0].value = %(name)s_marker.getLatLng().lat();
            $('#id_longitude')[0].value = %(name)s_marker.getLatLng().lng();
            GEvent.addListener(%(name)s_marker, "dragend", function() {
                var point = %(name)s_marker.getLatLng();
                $('#id_latitude')[0].value = point.lat();
                $('#id_longitude')[0].value = point.lng();
            });
    }});
    $(document).unload(function () {GUnload()});
</script>
''' % dict(name=name)
        html = "<div id=\"map_%s\" style=\"width: 100%%; height: 300px\"></div>" % name
        return mark_safe(js+html)

