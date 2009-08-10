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
        html = '<input type="hidden" name="%(name)s" id="id_%(name)s" value="%(value)s">' % dict(name=name, value=value)
        html += "<div id='map'></div>"
        return mark_safe(html)

