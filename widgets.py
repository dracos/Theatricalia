from django.utils import dateformat
from django.forms.widgets import Input
from datetime import date

class PrettyDateInput(Input):
    input_type = 'text'

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        elif isinstance(value, date):
            value = dateformat.format(value, "jS F Y")
        return super(PrettyDateInput, self).render(name, value, attrs)

