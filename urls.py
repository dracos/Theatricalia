import os
import settings

from django.conf.urls.defaults import *
from django.views.generic import date_based, simple

from views import *
from profiles import views as profiles
from plays import views as plays
from productions import views as productions
from people import views as people
from places import views as places
from search import views as search
from photos import views as photos
from common import views as common
from merged import views as merged
from news import views as news
from news.models import Article

from django.contrib import admin
admin.autodiscover()

from feeds import PersonFeed, PlayFeed, PlaceFeed, NearbyFeed, UserSeenFeed, NewsFeed, view as feeds_view

urlpatterns = patterns('',
    # Example:
    # (r'^theatricalia/', include('theatricalia.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^admin/(.*)', admin.site.root),

    url(r'^tickets/boxoffice$', profiles.register, name='register'),
    url(r'^tickets/(?P<uidb32>[0-9A-Za-z]+)-(?P<token>.+)$', profiles.register_confirm, name='register-confirm'),
    url(r'^tickets$', profiles.login, name='login'),
    url(r'^tickets/exchange$', 'django.contrib.auth.views.password_change', name='password-change'),
    (r'^tickets/exchanged$', 'django.contrib.auth.views.password_change_done'),
    url(r'^tickets/lost$', 'django.contrib.auth.views.password_reset', name='password-reset'),
    (r'^tickets/lost/done$', 'django.contrib.auth.views.password_reset_done'),
    (r'^tickets/lost/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)$', 'django.contrib.auth.views.password_reset_confirm'),
    (r'^tickets/lost/found$', 'django.contrib.auth.views.password_reset_complete'),
    url(r'^tickets/returns$', 'django.contrib.auth.views.logout', name='logout'),

    url('^$', home, name='home'),

    url('^about$', static_about, name='about'),
    url('^assistance$', static_help, name='help'),
    url('^criticism$', static_contact, name='criticism'),
    url('^colophon$', static_colophon, name='colophon'),
    url('^moo$', static_moocards, name='moo'),

    url('^(?P<url>(play|person|place|around)/.*)/feed$', feeds_view,
        { 'feed_dict': {
        'person': PersonFeed,
        'play': PlayFeed,
        'place': PlaceFeed,
        'around': NearbyFeed,
        } },
    ),
    url('^(?P<url>profile/.*)/feed/seen$', feeds_view,
        { 'feed_dict': {
        'profile': UserSeenFeed,
        } },
    ),
    url('^around/(.*?)/alert/(add|remove)$', common.alert, name='around-alert'),

    url('^play/.*?/(?P<url>production/.*/merge)$', merged.merge),
    url('^(?P<url>(play|person|place|company)/.*)/merge$', merged.merge),

    url('^d/(?P<production_id>.+)$', productions.production_short_url),
    url('^production/(?P<production_id>.+)$', productions.production_short_url),
    url('^c/(?P<company_id>.+)$', productions.production_company_short_url),
    url('^p/(?P<play_id>.+)$', plays.play_short_url),
    url('^t/(?P<place_id>.+)$', places.place_short_url),
    url('^a/(?P<person_id>.+)$', people.person_short_url),

    url('^api/(?P<type>production|play|place|company|person)/(?P<id>[^/]+)/flickr$', common.api_flickr),

    url('^plays$', plays.list_plays, name='plays_all'),
    url('^plays/(?P<letter>[a-z0*])$', plays.list_plays, name='plays'),
    url('^play/(?P<play_id>.*?)/(?P<play>.*)/alert/(?P<type>add|remove)$', plays.play_alert, name='play-alert'),
    url('^play/(?P<play_id>.*?)/(?P<play>.*?)/production/(?P<production_id>[0-9a-z]+)/seen/(?P<type>add|remove)$', productions.production_seen, name='production-seen'),
    url('^play/(?P<play_id>.*?)/(?P<play>.*?)/production/(?P<production_id>[0-9a-z]+)/edit$', productions.production_edit, name='production-edit'),
    url('^play/(?P<play_id>.*?)/(?P<play>.*?)/production/(?P<production_id>[0-9a-z]+)/edit/cast$', productions.production_edit_cast, name='production-edit-cast'),
    url('^play/(?P<play_id>.*?)/(?P<play>.*?)/production/(?P<production_id>[0-9a-z]+)/edit/(?P<part_id>[0-9]+)$', productions.part_edit, name='part-edit'),
    url('^play/(?P<play_id>.*?)/(?P<play>.*?)/production/(?P<production_id>[0-9a-z]+)/corrected$', productions.production_corrected, name='production-corrected'),
    url('^play/(?P<play_id>.*?)/(?P<play>.*?)/production/(?P<production_id>[0-9a-z]+).(?P<format>json)$', productions.production, name='production-json'),
    url('^play/(?P<play_id>.*?)/(?P<play>.*?)/production/(?P<production_id>[0-9a-z]+)$', productions.production, name='production'),
    url('^play/(?P<play_id>.*?)/(?P<play>.*)/future$', plays.play_productions, {'type':'future'}, name='play-productions-future'),
    url('^play/(?P<play_id>.*?)/(?P<play>.*)/past$', plays.play_productions, {'type':'past'}, name='play-productions-past'),
    url('^play/(?P<play_id>.*?)/(?P<play>.*)/edit$', plays.play_edit, name='play-edit'),
    url('^play/(?P<play_id>.*?)/(?P<play>.*)/add$', productions.add_from_play, name='play-production-add'),
    url('^play/(?P<play_id>.*?)/(?P<play>.*)$', plays.play, name='play'),
    url('^play/(?P<play_id>.+)$', plays.play_short_url),

    # url('^play/(?P<play>.*?)/part/(?P<part>.*)$', productions.by_part),

    url('^people$', people.list_people, name='people_all'),
    url('^people/(?P<letter>[a-z0*])$', people.list_people, name='people'),
    url('^person/(?P<person_id>.*?)/(?P<person>.*)/future$', people.person_productions, {'type':'future'}, name='person-productions-future'),
    url('^person/(?P<person_id>.*?)/(?P<person>.*)/past$', people.person_productions, {'type':'past'}, name='person-productions-past'),
    url('^person/(?P<person_id>.*?)/(?P<person>.*)/edit$', people.person_edit, name='person-edit'),
    url('^person/(?P<person_id>.*?)/(?P<person>.*)/alert/(?P<type>add|remove)$', people.person_alert, name='person-alert'),
    url('^person/(?P<person_id>.*?)/(?P<person>.*)\.js$', people.person_js, name='person-json'),
    url('^person/(?P<person_id>.*?)/(?P<person>.*)$', people.person, name='person'),
    url('^person/(?P<person_id>.+)$', people.person_short_url),

    url('^places$', places.list_places, name='places_all'),
    url('^places/(?P<letter>[a-z0*])$', places.list_places, name='places'),
    url('^place/(?P<place_id>[^/]+)/(?P<place>.*)/future$', places.place_productions, {'type':'future'}, name='place-productions-future'),
    url('^place/(?P<place_id>[^/]+)/(?P<place>.*)/past$', places.place_productions, {'type':'past'}, name='place-productions-past'),
    url('^place/(?P<place_id>[^/]+)/(?P<place>.*)/edit$', places.place_edit, name='place-edit'),
    url('^place/(?P<place_id>[^/]+)/(?P<place>.*)/alert/(?P<type>add|remove)$', places.place_alert, name='place-alert'),
    url('^place/(?P<place_id>[^/]+)/(?P<place>.*)/add$', productions.add_from_place, name='place-production-add'),
    url('^place/(?P<place_id>[^/]+)/(?P<place>.*)/productions$', places.productions, name='place-productions'),
    url('^place/(?P<place_id>[^/]+)/(?P<place>.*)/people$', places.people, name='place-people'),
    url('^place/(?P<place_id>[^/]+)/(?P<place>[^/]*)$', places.place, name='place'),
    url('^place/(?P<place_id>[^/]+)$', places.place_short_url),

    url('^company/(?P<company_id>[^/]+)/(?P<company>.*)/future$', productions.company_productions, {'type':'future'}, name='company-productions-future'),
    url('^company/(?P<company_id>[^/]+)/(?P<company>.*)/past$', productions.company_productions, {'type':'past'}, name='company-productions-past'),
    url('^company/(?P<company_id>[^/]+)/(?P<company>.*)/edit$', productions.company_edit, name='company-edit'),
    url('^company/(?P<company_id>[^/]+)/(?P<company>.*)/alert/(?P<type>add|remove)$', productions.company_alert, name='company-alert'),
    url('^company/(?P<company_id>[^/]+)/(?P<company>.*)/add$', productions.add_from_company, name='company-production-add'),
    url('^company/(?P<company_id>[^/]+)/(?P<company>[^/]*)$', productions.company, name='company'),
    url('^company/(?P<company_id>[^/]+)$', productions.production_company_short_url),

    url('^observations/post/', productions.post_comment_wrapper),
    url('^observations/', include('django.contrib.comments.urls')),
    url('^photograph/take/', photos.take_photo, name='take-photo'),
    url('^photograph/taken/', photos.photo_taken, name='photo-taken'),
    url('^photograph/view/(?P<photo_id>[0-9a-z]+)$', photos.view, name='photo-view'),

    url('^search/around/(?P<search>.+)/future$', search.search_around, {'type':'future'}, name='search-around-future'),
    url('^search/around/(?P<search>.+)/past$', search.search_around, {'type':'past'}, name='search-around-past'),
    url('^search/around/(?P<search>.+)$', search.search_around, name='search-around'),
    url('^search/parts/(?P<search>.+)$', search.search_parts, name='search-parts'),
    url('^search$', search.search, name='search'),

    url('^ajax/autocomplete$', search.search_autocomplete, name='search-autocomplete'),

    url('^add$', productions.production_add, name='production-add'),

    url('^profile/alert/(?P<id>l?\d+)$', profiles.profile_alert, name='profile-alert-remove'),
    url('^profile/alert$', profiles.profile_alert, name='profile-alert'),
    url('^profile/edit$', profiles.profile_edit, name='profile-edit'),
    url('^profile/(?P<username>.*)$', profiles.profile, name='profile'),
    url('^profile$', profiles.profile_user, name='profile-user'),

    url('^(?P<url>publicity)/feed$', 'django.contrib.syndication.views.feed',
        { 'feed_dict': {
        'publicity': NewsFeed,
        } },
    ),
    url('^publicity$', news.index, name='news-index'),
    url('^publicity/(?P<year>\d{4})$', news.year, name='news-year'),
    url('^publicity/(?P<year>\d{4})/(?P<month>\w+)$', news.month, name='news-month'),
    url('^publicity/(?P<year>\d{4})/(?P<month>\w+)/(?P<slug>[-\w]+)$',
        news.article, name='news-entry'),

    #url('forums/forum/', include('forums.django-forum.forum.urls')),
    #url('forums/simple/', include('forums.django-simpleforum.forum.urls')),
    #url('forums/bb/', include('forums.djangobb.djangobb.urls')),
    #url('forums/counterpoint/', include('forums.counterpoint.counterpoint.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('', 
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': os.path.join(settings.OUR_ROOT, 'static')
        })
    )
    

