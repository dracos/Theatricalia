from django.template.defaultfilters import slugify

# Miss out i l o u
digits = "0123456789abcdefghjkmnpqrstvwxyz"

def base32_to_int(s):
    """Convert a base 32 string to an integer"""
    decoded = 0
    multi = 1
    while len(s) > 0:
        decoded += multi * digits.index(s[-1:])
        multi = multi * 32
        s = s[:-1]
    return decoded

def int_to_base32(i):
    """Converts an integer to a base32 string"""
    enc = ''
    while i>=32:
        i, mod = divmod(i,32)
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

