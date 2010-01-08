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

def add_play(title, force_insert=False):
    if force_insert:
        play = Play(title=title)
        if not dry_run:
            play.save()
        return play
    try:
        play = Play.objects.get(title__iexact=title, authors=None)
    except:
        play = Play(title=title)
        if not dry_run:
            play.save()
    return play

def add_theatre(theatre, town=''):
    theatre = re.sub('^(A|An|The) (.*)$', r'\2, \1', theatre.strip())
    theatre_no_the = re.sub(', (A|An|The)$', '', theatre)
    theatre_with_the = '%s, The' % theatre_no_the
    town = town.strip()
    try:
        location = Place.objects.get(name=theatre_with_the, town=town)
        log("Found place %s" % location)
    except:
        try:
            location = Place.objects.get(name=theatre_no_the, town=town)
            log("Found place %s" % location)
        except:
            if dry_run:
                print "Going to get_or_create place %s, %s" % (theatre, town)
                location = Place(name=theatre, town=town)
            else:
                location, created = Place.objects.get_or_create(name=theatre, town=town)
    return location
