import re
from django import template
#from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe, SafeData
from django.template.defaultfilters import stringfilter

register = template.Library()

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
    str = re.sub('\s-\s', ' &ndash; ', str)
    str = re.sub('(\d)-(\d)', r'\1&ndash;\2', str)
    str = str.replace('--', '&ndash;').replace('---', '&mdash;')
    str = re.sub('\. ?\. ?\.', '&hellip;', str)

    # Nice quotes
    str = str.replace('``', '&ldquo;').replace("''", '&rdquo;')
    if str.find('<') == -1:
        str = re.sub('"([^"]*)"', r'&ldquo;\1&rdquo;', str)
        str = re.sub("'(.*?)'(?=[^\w]|$)", r'&lsquo;\1&rsquo;', str)
        str = str.replace('"', '&quot;').replace("'", '&rsquo;')
    else:
        # Must be Safe data with HTML tags in it
        lines = []
        for line in re.split('(<[^>]*>)', str):
            if not re.match('<[^>]*>', line):
                line = re.sub('"([^"]*)"', r'&ldquo;\1&rdquo;', line)
                line = re.sub("'(.*?)'(?=[^\w]|$)", r'&lsquo;\1&rsquo;', line)
                line = line.replace('"', '&quot;').replace("'", '&rsquo;')
            lines.append(line)
        str = ''.join(lines)
    #str = re.sub("'([dlstv])", r'&rsquo;\1', str) # Nice apostrophe
    #str = re.sub("s'\s", r's&rsquo; ', str) # Nice apostrophe
    #str = re.sub("O'", r'O&rsquo;', str) # Nice apostrophe

    str = re.sub(r'\b(\d+)(st|nd|rd|th)\b', r'\1<sup>\2</sup>', str) # Nice ordinals
    str = re.sub(r'([A-Z]\.)\s+(?=[A-Z])', r'\1&#8201;', str) # Hair or thin spaces between intermediary periods
    str = re.sub(r'\b([A-Z]{3,})\b', r'<abbr>\1</abbr>', str) # Letterspace strings of capitals (no digits due to postcodes, for now)

    # Nice small numbers
    str = re.sub(r'\s1\s', ' one ', str)
    str = re.sub(r'\s2\s', ' two ', str)
    str = re.sub(r'\s3\s', ' three ', str)
    str = re.sub(r'\s4\s', ' four ', str)
    str = re.sub(r'\s5\s', ' five ', str)
    str = re.sub(r'\s6\s', ' six ', str)
    str = re.sub(r'\s7\s', ' seven ', str)
    str = re.sub(r'\s8\s', ' eight ', str)
    str = re.sub(r'\s9\s', ' nine ', str)
    str = re.sub(r'\s0\s', ' zero ', str)
    str = re.sub(r'^1\s', 'One ', str)
    str = re.sub(r'^2\s', 'Two ', str)
    str = re.sub(r'^3\s', 'Three ', str)
    str = re.sub(r'^4\s', 'Four ', str)
    str = re.sub(r'^5\s', 'Five ', str)
    str = re.sub(r'^6\s', 'Six ', str)
    str = re.sub(r'^7\s', 'Seven ', str)
    str = re.sub(r'^8\s', 'Eight ', str)
    str = re.sub(r'^9\s', 'Nine ', str)
    str = re.sub(r'^0\s', 'Zero ', str)

    str = re.sub(r'(\s[0-9.,]+) ([A-Za-z])', r'\1&nbsp;\2', str) # Hard space short numerical and maths expressions
    str = re.sub(r' ([0-9][A-Z][A-Z])', r'&nbsp;\1', str)

    str = re.sub('\(press night\)', '<small>(press night)</small>', str)

    return mark_safe(str)

@register.filter
@stringfilter
def prettify_num(num):
    num = re.sub('(?<=\d)(?=(\d\d\d)+([^0-9]|$))', ',', num)
    return num
    
@register.filter
def prettify_list(list):
    if not list: return ''
    if isinstance(list, str): return list
    num = len(list)
    list = [ prettify(x) for x in list ]
    if num > 2:
        s = ', '.join(list[:num-2]) + ', ' + ', and '.join(list[num-2:])
    elif num == 2:
        s = ' and '.join(list)
    elif num == 1:
        s = list[0]
    else:
        s = ''
    return s
