import re, urllib
from os.path import basename
from django.core.files.base import ContentFile
from places.models import Place
from plays.models import Play
from photos.models import Photo

dry_run = True

def dry_run():
    return dry_run

def real_run():
    global dry_run
    dry_run = False

def log(s):
    print s

def add_photo(url, object, title=''):
    logo = Photo( title = title, content_object = object )
    log('"%s" photo from %s' % (title, url))
    if not dry_run:
        u = urllib.urlopen(url).read()
        logo.photo.save(basename(url), ContentFile(u))

# Only works without authors at present
def add_play(title, force_insert=False):
    title = re.sub('^(A|An|The) (.*)$', r'\2, \1', title)
    if force_insert:
        play = Play(title=title)
        if not dry_run:
            play.save()
        return play
    play = Play.objects.filter(title__iexact=title).order_by('id')
    if play:
        return play[0]
    play = Play(title=title)
    if not dry_run:
        play.save()
    return play

def add_theatre(theatre, town=''):
    theatre = re.sub('^(A|An|The) (.*)$', r'\2, \1', theatre.strip())
    theatre_no_the = re.sub(', (A|An|The)$', '', theatre)
    theatre_with_the = '%s, The' % theatre_no_the
    town = town.strip()

    def a_try(**attrs):
        location = Place.objects.get(**attrs)
        log("Found place %s" % location)
        return location

    try:
        return a_try(name=theatre_with_the, town=town)
    except:
        pass

    try:
        return a_try(name=theatre_no_the, town=town)
    except:
        pass

    try:
        return a_try(name='%s, %s' % (theatre_no_the, town), town=town)
    except:
        pass

    try:
        return a_try(name='%s, %s' % (theatre_no_the, town))
    except:
        pass

    if dry_run:
        print "Going to get_or_create place %s, %s" % (theatre, town)
        location = Place(name=theatre, town=town)
    else:
        location, created = Place.objects.get_or_create(name=theatre, town=town)
    return location

