import copy
import datetime
import re
import time
from datetime import date
from widgets import PrettyDateInput
from django.db import models
from django import forms
from django.forms import ValidationError
from django.utils import dateformat


class ApproximateDate(object):
    """A date that accepts 0 for month or day to mean we don't know when it is within that month/year.
       Also works with BC dates."""
    def __init__(self, year, month=0, day=0):
        self.bc = False
        absyear = year
        if year < 0:
            absyear = -year
            self.bc = True
        if year and month and day:
            date(absyear, month, day)
        elif year and month:
            date(absyear, month, 1)
        elif year and day:
            raise ValueError("You cannot specify just a year and a day")
        elif year:
            date(absyear, 1, 1)
        else:
            raise ValueError("You must specify a year")
        self.year = year
        self.month = month
        self.day = day

    def __repr__(self):
        if self.year and self.month and self.day:
            return "%04d-%02d-%02d" % (self.year, self.month, self.day)
        elif self.year and self.month:
            return "%04d-%02d-00" % (self.year, self.month)
        elif self.year:
            return "%04d-00-00" % (self.year)

    def __len__(self):
        return len(repr(self))

    def __str__(self):
        absself = copy.copy(self)
        if absself.year < 0:
            absself.year = -absself.year
        if self.year and self.month and self.day:
            out = dateformat.format(absself, "jS F Y")
        elif self.year and self.month:
            out = dateformat.format(absself, "F Y")
        elif self.year:
            out = dateformat.format(absself, "Y")
        if self.bc:
            out += " BC"
        return out

    def __lt__(self, other):
        if other is None or (self.year, self.month, self.day) >= (other.year, other.month, other.day):
            return False
        return True

    def __le__(self, other):
        if other is None or (self.year, self.month, self.day) > (other.year, other.month, other.day):
            return False
        return True

    def __gt__(self, other):
        if other is None or (self.year, self.month, self.day) <= (other.year, other.month, other.day):
            return False
        return True

    def __ge__(self, other):
        if other is None or (self.year, self.month, self.day) < (other.year, other.month, other.day):
            return False
        return True


ansi_date_re = re.compile(r'^-?\d{4}-\d{1,2}-\d{1,2}$')


class ApproximateDateField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 10
        super(ApproximateDateField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(ApproximateDateField, self).deconstruct()
        del kwargs["max_length"]
        return name, path, args, kwargs

    def to_python(self, value):
        if isinstance(value, ApproximateDate):
            return value

        return self.from_db_value(value)

    def from_db_value(self, value, *args, **kwargs):
        if value in (None, ''):
            return None
        # if isinstance(value, datetime.datetime):
        #     value = value.date().isoformat()
        # if isinstance(value, datetime.date):
        #     value = value.isoformat()

        if not ansi_date_re.search(value):
            raise ValidationError('Enter a valid date in YYYY-MM-DD format.')

        year, month, day = list(map(int, value.rsplit('-', 2)))
        try:
            return ApproximateDate(year, month, day)
        except ValueError as e:
            msg = 'Invalid date: %s' % str(e)
            raise ValidationError(msg)

    def get_prep_value(self, value):
        if value in (None, ''):
            return ''
        if isinstance(value, ApproximateDate):
            return repr(value)
        if isinstance(value, date):
            return dateformat.format(value, "Y-m-d")
        if not ansi_date_re.search(value):
            raise ValidationError('Enter a valid date in YYYY-MM-DD format.')
        return value

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)

    def formfield(self, **kwargs):
        defaults = {'form_class': ApproximateDateFormField}
        defaults.update(kwargs)
        return super(ApproximateDateField, self).formfield(**defaults)


DATE_INPUT_FORMATS = (
    '%Y-%m-%d', '%d/%m/%Y', '%d/%m/%y',  # '2006-10-25', '25/10/2006', '25/10/06'
    '%b %d %Y', '%b %d, %Y',             # 'Oct 25 2006', 'Oct 25, 2006'
    '%d %b %Y', '%d %b, %Y',             # '25 Oct 2006', '25 Oct, 2006'
    '%B %d %Y', '%B %d, %Y',             # 'October 25 2006', 'October 25, 2006'
    '%d %B %Y', '%d %B, %Y',             # '25 October 2006', '25 October, 2006'
)
MONTH_INPUT_FORMATS = (
    '%m/%Y',                         # '10/2006'
    '%b %Y', '%Y %b',                # 'Oct 2006', '2006 Oct'
    '%B %Y', '%Y %B',                # 'October 2006', '2006 October'
)
YEAR_INPUT_FORMATS = (
    '%Y',                               # '2006'
)

BC_DATE_INPUT_FORMATS = [i.replace('%Y', '%Y BC') for i in DATE_INPUT_FORMATS]
BC_MONTH_INPUT_FORMATS = [i.replace('%Y', '%Y BC') for i in MONTH_INPUT_FORMATS]
BC_YEAR_INPUT_FORMATS = [i.replace('%Y', '%Y BC') for i in YEAR_INPUT_FORMATS]

BC_DATE_INPUT_FORMATS.extend([i.replace('%Y', '-%Y') for i in DATE_INPUT_FORMATS])
BC_MONTH_INPUT_FORMATS.extend([i.replace('%Y', '-%Y') for i in MONTH_INPUT_FORMATS])
BC_YEAR_INPUT_FORMATS.extend([i.replace('%Y', '-%Y') for i in YEAR_INPUT_FORMATS])


class ApproximateDateFormField(forms.fields.Field):
    def __init__(self, max_length=10, empty_value='', *args, **kwargs):
        super(ApproximateDateFormField, self).__init__(*args, **kwargs)

    def clean(self, value):
        super(ApproximateDateFormField, self).clean(value)
        if value in (None, ''):
            return None
        if isinstance(value, ApproximateDate):
            return value
        value = re.sub(r'(?<=\d)(st|nd|rd|th)', '', value.strip())
        for format in DATE_INPUT_FORMATS:
            try:
                match = time.strptime(value, format)
                return ApproximateDate(match[0], match[1], match[2])
            except ValueError:
                continue
        for format in MONTH_INPUT_FORMATS:
            try:
                match = time.strptime(value, format)
                return ApproximateDate(match[0], match[1], 0)
            except ValueError:
                continue
        for format in YEAR_INPUT_FORMATS:
            try:
                match = time.strptime(value, format)
                return ApproximateDate(match[0], 0, 0)
            except ValueError:
                continue
        for format in BC_DATE_INPUT_FORMATS:
            try:
                match = time.strptime(value, format)
                return ApproximateDate(-match[0], match[1], match[2])
            except ValueError:
                continue
        for format in BC_MONTH_INPUT_FORMATS:
            try:
                match = time.strptime(value, format)
                return ApproximateDate(-match[0], match[1], 0)
            except ValueError:
                continue
        for format in BC_YEAR_INPUT_FORMATS:
            try:
                match = time.strptime(value, format)
                return ApproximateDate(-match[0], 0, 0)
            except ValueError:
                continue
        raise ValidationError('Please enter a valid date.')


# PrettyDateField - same as DateField but accepts more input, like ApproximateDateFormField above
class PrettyDateField(forms.fields.Field):
    widget = PrettyDateInput

    def clean(self, value):
        """
        Validates that the input can be converted to a date. Returns a Python
        datetime.date object.
        """
        super(PrettyDateField, self).clean(value)
        if value in (None, ''):
            return None
        if isinstance(value, datetime.datetime):
            return value.date()
        if isinstance(value, datetime.date):
            return value
        value = re.sub(r'(?<=\d)(st|nd|rd|th)', '', value.strip())
        for format in DATE_INPUT_FORMATS:
            try:
                return datetime.date(*time.strptime(value, format)[:3])
            except ValueError:
                continue
        raise ValidationError('Please enter a valid date.')
