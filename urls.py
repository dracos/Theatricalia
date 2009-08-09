import os
import settings

from django.conf.urls.defaults import *

from views import *
from profiles import views as profiles
from plays import views as plays
from productions import views as productions
from people import views as people
from places import views as places
from search import views as search
from photos import views as photos

from django.contrib import admin
admin.autodiscover()

from feeds import PersonFeed, PlayFeed, PlaceFeed

urlpatterns = patterns('',
    # Example:
    # (r'^theatredb/', include('theatredb.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^admin/(.*)', admin.site.root),

    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': os.path.join(settings.OUR_ROOT, 'static')
    }),
    
    url(r'^tickets/boxoffice$', profiles.register, name='register'),
    url(r'^tickets/(?P<uidb32>[0-9A-Za-z]+)-(?P<token>.+)$', profiles.register_confirm, name='register-confirm'),
    url(r'^tickets$', profiles.login, name='login'),
    url(r'^tickets/exchange$', 'django.contrib.auth.views.password_change', name='password-change'),
    (r'^tickets/exchanged$', 'django.contrib.auth.views.password_change_done'),
    url(r'^tickets/lost$', 'django.contrib.auth.views.password_reset', name='password-reset'),
    (r'^tickets/lost/done$', 'django.contrib.auth.views.password_reset_done'),
    (r'^tickets/lost/(?P<uidb32>[0-9A-Za-z]+)-(?P<token>.+)$', 'django.contrib.auth.views.password_reset_confirm'),
    (r'^tickets/lost/found$', 'django.contrib.auth.views.password_reset_complete'),
    url(r'^tickets/returns$', 'django.contrib.auth.views.logout', name='logout'),

    ('^$', home),

    url('^about$', static_about, name='about'),
    url('^help$', static_help, name='help'),
    url('^criticism$', static_contact, name='criticism'),
    url('^colophon$', static_colophon, name='colophon'),

    url('^(?P<url>(play|person|place)/.*)/feed$', 'django.contrib.syndication.views.feed',
        { 'feed_dict': {
		'person': PersonFeed,
		'play': PlayFeed,
		'place': PlaceFeed,
	} },
    ),

    url('^plays$', plays.list, name='plays_all'),
    url('^plays/(?P<letter>[a-z0*])$', plays.list, name='plays'),
    url('^play/(?P<play>.*?)/production/(?P<production_id>[0-9a-z]+)/edit$', productions.production_edit, name='production-edit'),
    url('^play/(?P<play>.*?)/production/(?P<production_id>[0-9a-z]+)/edit/cast$', productions.production_edit_cast, name='production-edit-cast'),
    url('^play/(?P<play>.*?)/production/(?P<production_id>[0-9a-z]+)/edit/(?P<part_id>[0-9]+)$', productions.part_edit, name='part-edit'),
    url('^play/(?P<play>.*?)/production/(?P<production_id>[0-9a-z]+)$', productions.production, name='production'),
    url('^play/(?P<play>.*)/future$', plays.play_productions, {'type':'future'}, name='play-productions-future'),
    url('^play/(?P<play>.*)/past$', plays.play_productions, {'type':'past'}, name='play-productions-past'),
    url('^play/(?P<play>.*)/edit$', plays.play_edit, name='play-edit'),
    url('^play/(?P<play>.*)$', plays.play, name='play'),

    # url('^play/(?P<play>.*?)/part/(?P<part>.*)$', productions.by_part),

    url('^people$', people.list, name='people_all'),
    url('^people/(?P<letter>[a-z0*])$', people.list, name='people'),
    url('^person/(?P<person_id>.*?)/(?P<person>.*)/future$', people.person_productions, {'type':'future'}, name='person-productions-future'),
    url('^person/(?P<person_id>.*?)/(?P<person>.*)/past$', people.person_productions, {'type':'past'}, name='person-productions-past'),
    url('^person/(?P<person_id>.*?)/(?P<person>.*)/edit$', people.person_edit, name='person-edit'),
    url('^person/(?P<person_id>.*?)/(?P<person>.*)\.js$', people.person_js, name='person-json'),
    url('^person/(?P<person_id>.*?)/(?P<person>.*)$', people.person, name='person'),

    url('^places$', places.list, name='places_all'),
    url('^places/(?P<letter>[a-z0*])$', places.list, name='places'),
    url('^place/(?P<place_id>.+?)/(?P<place>.*)/future$', places.place_productions, {'type':'future'}, name='place-productions-future'),
    url('^place/(?P<place_id>.+?)/(?P<place>.*)/past$', places.place_productions, {'type':'past'}, name='place-productions-past'),
    url('^place/(?P<place_id>.+?)/(?P<place>.*)/edit$', places.place_edit, name='place-edit'),
    url('^place/(?P<place_id>.+?)/(?P<place>.*)$', places.place, name='place'),

    url('^productions/(?P<production>.*)$', productions.by_company, name='company'),

    url('^observations/post/', productions.post_comment_wrapper),
    url('^observations/', include('django.contrib.comments.urls')),
    url('^photograph/take/', photos.take_photo, name='take-photo'),
    url('^photograph/taken/', photos.photo_taken, name='photo-taken'),
    url('^photograph/view/(?P<photo_id>[0-9a-z]+)$', photos.view, name='photo-view'),

    url('^search$', search.search, name='search'),
)
