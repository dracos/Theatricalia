from django.template.defaultfilters import slugify

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
