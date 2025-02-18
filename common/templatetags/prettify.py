import re
from django import template
# from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe, SafeData
from django.template.defaultfilters import stringfilter

register = template.Library()


def smart_quotes(s):
    s = re.sub(r'(?:(?<=\A)|(?<=[([{"\-]|\s))\'', '&lsquo;', s)
    s = re.sub(r'(?<!\s)\'(?!\Z|[.,:;!?"\'(){}[\]\-]|\s)', '&rsquo;', s)
    s = re.sub('"([^"]*)"', r'&ldquo;\1&rdquo;', s)
    s = s.replace('"', '&quot;').replace("'", '&rsquo;')
    return s


@register.filter
@stringfilter
def prettify(str):
    # Assume that autoescape is always on
    # Do our own conditional_escape, as we want to do it in parts

    # Escape first, but don't do ' and " as we're going to be changing them
    if not isinstance(str, SafeData):
        str = str.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    # Escaped, for if you really want them
    str = str.replace(r'\'', '&#39;').replace(r'\"', '&quot;').replace(r'\\', '\\')

    # Nice dashes and ellipses
    str = re.sub(r'\s-\s', ' &ndash; ', str)
    str = re.sub(r'(\d)-(\d)', r'\1&ndash;\2', str)
    str = str.replace('--', '&ndash;').replace('---', '&mdash;')
    str = re.sub(r'\. ?\. ?\.', '&hellip;', str)

    # Nice quotes
    str = str.replace('``', '&ldquo;').replace("''", '&rdquo;')
    cockney = ["'tain't", "'twere", "'twas", "'tis", "'twill", "'til", "'bout", "'nuff", "'round", "'cause", "'em"]
    str = re.sub('(?i)' + '|'.join(cockney), lambda x: x.group(0).replace("'", '&rsquo;'), str)
    if str.find('<') == -1:
        str = smart_quotes(str)
    else:
        # Must be Safe data with HTML tags in it
        lines = []
        for line in re.split('(<[^>]*>)', str):
            if not re.match('<[^>]*>', line):
                line = smart_quotes(line)
            lines.append(line)
        str = ''.join(lines)
    # str = re.sub("'([dlstv])", r'&rsquo;\1', str) # Nice apostrophe
    # str = re.sub("s'\s", r's&rsquo; ', str) # Nice apostrophe
    # str = re.sub("O'", r'O&rsquo;', str) # Nice apostrophe

    str = re.sub(r'\b(\d+)(st|nd|rd|th)\b', r'\1<sup>\2</sup>', str)  # Nice ordinals
    str = re.sub(r'([A-Z]\.)\s+(?=[A-Z])', r'\1&#8201;', str)  # Hair or thin spaces between intermediary periods
    # Letterspace strings of capitals (no digits due to postcodes, for now)
    str = re.sub(r'\b([A-Z]{3,})\b', r'<abbr>\1</abbr>', str)

    # Nice small numbers
    # str = re.sub(r'\s1\s', ' one ', str)
    # str = re.sub(r'\s2\s', ' two ', str)
    # str = re.sub(r'\s3\s', ' three ', str)
    # str = re.sub(r'\s4\s', ' four ', str)
    # str = re.sub(r'\s5\s', ' five ', str)
    # str = re.sub(r'\s6\s', ' six ', str)
    # str = re.sub(r'\s7\s', ' seven ', str)
    # str = re.sub(r'\s8\s', ' eight ', str)
    # str = re.sub(r'\s9\s', ' nine ', str)
    # str = re.sub(r'\s0\s', ' zero ', str)
    # str = re.sub(r'^1\s', 'One ', str)
    # str = re.sub(r'^2\s', 'Two ', str)
    # str = re.sub(r'^3\s', 'Three ', str)
    # str = re.sub(r'^4\s', 'Four ', str)
    # str = re.sub(r'^5\s', 'Five ', str)
    # str = re.sub(r'^6\s', 'Six ', str)
    # str = re.sub(r'^7\s', 'Seven ', str)
    # str = re.sub(r'^8\s', 'Eight ', str)
    # str = re.sub(r'^9\s', 'Nine ', str)
    # str = re.sub(r'^0\s', 'Zero ', str)

    str = re.sub(r'(\s[0-9.,]+) ([A-Za-z])', r'\1&#8239;\2', str)  # Hard space short numerical and maths expressions
    str = re.sub(r' ([0-9][A-Z][A-Z])', r'&#8239;\1', str)

    str = re.sub(r'\(press night\)', '<small>(press night)</small>', str)

    str = re.sub('/media/audio/[^ ]*', r'<a href="https://theatricalia.com\g<0>">\g<0></a>', str)

    str = re.sub('https://(?:www.)?instagram.com/p/(.*?)/', r'''\g<0>
<iframe src="//www.instagram.com/p/\1/embed/?cr=1&amp;v=14&amp;wp=1080" allowtransparency="true" allowfullscreen="true" frameborder="0" height="639" scrolling="no" style="background: white; max-width: 540px; width: calc(100% - 2px); border-radius: 3px; border: 1px solid rgb(219, 219, 219); box-shadow: none; display: block; margin: 0px 0px 12px; min-width: 326px; padding: 0px;"></iframe>
''', str)

    return mark_safe(str)


@register.filter
@stringfilter
def prettify_num(num):
    num = re.sub(r'(?<=\d)(?=(\d\d\d)+([^0-9]|$))', ',', num)
    return num


@register.filter
def prettify_list(list):
    if not list:
        return ''
    if isinstance(list, str):
        return list
    num = len(list)
    list = [prettify(x) for x in list]
    if num > 2:
        s = u', '.join(list[:num-2]) + u', ' + u', and '.join(list[num-2:])
    elif num == 2:
        s = u' and '.join(list)
    elif num == 1:
        s = list[0]
    else:
        s = u''
    return s


@register.filter
@stringfilter
def replace(s, v):
    return s.replace(v[0], v[1])
