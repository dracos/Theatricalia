from django.template.defaultfilters import slugify
from django.utils import dateformat

# Miss out i l o u
digits = "0123456789abcdefghjkmnpqrstvwxyz"


class MistypedIDException(Exception):
    pass


def base32_to_int(s):
    """Convert a base 32 string to an integer"""
    mistyped = False
    if s.find('o') > -1 or s.find('i') > -1 or s.find('l') > -1:
        s = s.replace('o', '0').replace('i', '1').replace('l', '1')
        mistyped = True
    decoded = 0
    multi = 1
    while len(s) > 0:
        decoded += multi * digits.index(s[-1:])
        multi = multi * 32
        s = s[:-1]
    if mistyped:
        raise MistypedIDException(decoded)
    return decoded


def int_to_base32(i):
    """Converts an integer to a base32 string"""
    enc = ''
    while i >= 32:
        i, mod = divmod(i, 32)
        enc = digits[mod] + enc
    enc = digits[i] + enc
    return enc


def unique_slugify(thing, s, instance=None):
    slug = slugify(s)
    slug0 = slug
    i = 2
    qs = thing.objects.all()
    if instance and instance.pk:
        qs = qs.exclude(pk=instance.pk)
    while qs.filter(slug=slug):
        slug = '%s-%s' % (slug0, i)
        i += 1
    return slug


def pretty_date_range(start_date, press_date, end_date):
    if not start_date:
        if not press_date:
            if not end_date:
                return 'dates unknown'
            else:
                return u'ended %s' % end_date
        elif not end_date:
            return '%s (press night)' % dateformat.format(press_date, 'jS F Y')

    if not end_date:
        return u'started %s' % start_date

    press = ''
    if not start_date and press_date:
        press = ' (press night)'
        start_date = press_date

    if dateformat.format(start_date, 'dmY') == dateformat.format(end_date, 'dmY'):
        date = end_date

    elif dateformat.format(start_date, 'mY') == dateformat.format(end_date, 'mY') and start_date.day and end_date.day:
        date = u'%s%s - %s' % (dateformat.format(start_date, 'jS'), press, end_date)
    elif dateformat.format(start_date, 'mY') == dateformat.format(end_date, 'mY') and start_date.day:
        date = u'%s%s - ? %s' % (dateformat.format(start_date, 'jS'), press, end_date)
    elif dateformat.format(start_date, 'mY') == dateformat.format(end_date, 'mY'):
        date = u'?%s - %s' % (press, end_date)

    elif start_date.year == end_date.year and start_date.day and end_date.month:
        date = u'%s%s - %s' % (dateformat.format(start_date, 'jS F'), press, end_date)
    elif start_date.year == end_date.year and start_date.day:
        date = u'%s%s - ? %s' % (dateformat.format(start_date, 'jS F'), press, end_date)
    elif start_date.year == end_date.year and start_date.month and end_date.month:
        date = u'%s%s - %s' % (dateformat.format(start_date, 'F'), press, end_date)
    elif start_date.year == end_date.year and start_date.month:
        date = u'%s%s - ? %s' % (dateformat.format(start_date, 'F'), press, end_date)
    elif start_date.year == end_date.year:
        date = u'?%s - %s' % (press, end_date)

    elif start_date.day:
        date = u'%s%s - %s' % (dateformat.format(start_date, 'jS F Y'), press, end_date)
    else:
        date = u'%s%s - %s' % (start_date, press, end_date)
    return date
    return date.replace(' ', u'\xa0').replace(u'\xa0-\xa0', ' - ')
