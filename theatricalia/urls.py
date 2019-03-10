import os
from django.conf import settings

from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import views
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
from django.contrib.auth import views as auth_views

from feeds import PersonFeed, PlayFeed, PlaceFeed, NearbyFeed, UserSeenFeed, NewsFeed

urlpatterns = [
    # Example:
    # (r'^theatricalia/', include('theatricalia.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', admin.site.urls),

    url(r'^tickets/boxoffice$', profiles.register, name='register'),
    url(r'^tickets/(?P<uidb32>[0-9A-Za-z]+)-(?P<token>.+)$', profiles.register_confirm, name='register-confirm'),
    url(r'^tickets$', profiles.login, name='login'),
    url(r'^tickets/exchange$', auth_views.password_change, name='password_change'),
    url(r'^tickets/exchanged$', auth_views.password_change_done, name='password_change_done'),
    url(r'^tickets/lost$', auth_views.password_reset, name='password_reset'),
    url(r'^tickets/lost/done$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^tickets/lost/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)$', auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^tickets/lost/found$', auth_views.password_reset_complete, name='password_reset_complete'),
    url(r'^tickets/returns$', auth_views.logout, name='logout'),

    url('^$', views.home, name='home'),

    url('^about$', views.static_about, name='about'),
    url('^assistance$', views.static_help, name='help'),
    url('^criticism$', views.static_contact, name='criticism'),
    url('^colophon$', views.static_colophon, name='colophon'),
    url('^moo$', views.static_moocards, name='moo'),

    url('^play/(?P<id>.*?)/(?P<slug>.*)/feed$', PlayFeed()),
    url('^person/(?P<id>.*?)/(?P<slug>.*)/feed$', PersonFeed()),
    url('^place/(?P<id>.*?)/(?P<slug>.*)/feed$', PlaceFeed()),
    url('^around/(?P<coord>.*)/feed$', NearbyFeed()),
    url('^profile/(?P<user>.*)/feed/seen$', UserSeenFeed()),

    url('^play/.*?/(?P<url>production/.*/merge)$', merged.merge),
    url('^(?P<url>(play|person|place|company)/.*)/merge$', merged.merge),

    url('^d/(?P<production_id>.+)$', productions.production_short_url),
    url('^production/(?P<production_id>.+)$', productions.production_short_url),
    url('^c/(?P<company_id>.+)$', productions.production_company_short_url),
    url('^p/(?P<play_id>.+)$', plays.play_short_url),
    url('^t/(?P<place_id>.+)$', places.place_short_url),
    url('^a/(?P<person_id>.+)$', people.person_short_url),

    url('^api/(?P<type>production|play|place|company|person)/(?P<id>[^/]+)/flickr$', common.api_flickr),

    url('^plays$', plays.PlayList.as_view(), name='plays_all'),
    url('^plays/(?P<letter>[a-z0*])$', plays.PlayList.as_view(), name='plays'),
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

    url('^people$', people.PersonList.as_view(), name='people_all'),
    url('^people/(?P<letter>[a-z0*])$', people.PersonList.as_view(), name='people'),
    url('^person/(?P<person_id>.*?)/(?P<person>.*)/future$', people.person_productions, {'type':'future'}, name='person-productions-future'),
    url('^person/(?P<person_id>.*?)/(?P<person>.*)/past$', people.person_productions, {'type':'past'}, name='person-productions-past'),
    url('^person/(?P<person_id>.*?)/(?P<person>.*)/edit$', people.person_edit, name='person-edit'),
    url('^person/(?P<person_id>.*?)/(?P<person>.*)\.js$', people.person_js, name='person-json'),
    url('^person/(?P<person_id>.*?)/(?P<person>.*)$', people.person, name='person'),
    url('^person/(?P<person_id>.+)$', people.person_short_url),

    url('^places$', places.PlaceList.as_view(), name='places_all'),
    url('^places/(?P<letter>[a-z0*])$', places.PlaceList.as_view(), name='places'),
    url('^place/(?P<place_id>[^/]+)/(?P<place>.*)/future$', places.place_productions, {'type':'future'}, name='place-productions-future'),
    url('^place/(?P<place_id>[^/]+)/(?P<place>.*)/past$', places.place_productions, {'type':'past'}, name='place-productions-past'),
    url('^place/(?P<place_id>[^/]+)/(?P<place>.*)/edit$', places.place_edit, name='place-edit'),
    url('^place/(?P<place_id>[^/]+)/(?P<place>.*)/add$', productions.add_from_place, name='place-production-add'),
    url('^place/(?P<place_id>[^/]+)/(?P<place>.*)/productions$', places.productions, name='place-productions'),
    url('^place/(?P<place_id>[^/]+)/(?P<place>.*)/people$', places.people, name='place-people'),
    url('^place/(?P<place_id>[^/]+)/(?P<place>[^/]*)$', places.place, name='place'),
    url('^place/(?P<place_id>[^/]+)$', places.place_short_url),

    url('^company/(?P<company_id>[^/]+)/(?P<company>.*)/future$', productions.company_productions, {'type':'future'}, name='company-productions-future'),
    url('^company/(?P<company_id>[^/]+)/(?P<company>.*)/past$', productions.company_productions, {'type':'past'}, name='company-productions-past'),
    url('^company/(?P<company_id>[^/]+)/(?P<company>.*)/edit$', productions.company_edit, name='company-edit'),
    url('^company/(?P<company_id>[^/]+)/(?P<company>.*)/add$', productions.add_from_company, name='company-production-add'),
    url('^company/(?P<company_id>[^/]+)/(?P<company>[^/]*)$', productions.company, name='company'),
    url('^company/(?P<company_id>[^/]+)$', productions.production_company_short_url),

    url('^observations/post/', productions.post_comment_wrapper),
    url('^observations/remove/(?P<comment_id>\d+)', productions.hide_comment, name='hide-comment'),
    url('^observations/', include('django_comments.urls')),
    url('^photograph/take/', photos.take_photo, name='take-photo'),
    url('^photograph/taken/', photos.photo_taken, name='photo-taken'),
    url('^photograph/view/(?P<photo_id>[0-9a-z]+)$', photos.view, name='photo-view'),

    url('^search/around/(?P<s>.+)/future$', search.search_around, {'type':'future'}, name='search-around-future'),
    url('^search/around/(?P<s>.+)/past$', search.search_around, {'type':'past'}, name='search-around-past'),
    url('^search/around/(?P<s>.+)$', search.search_around, name='search-around'),
    url('^search/parts/(?P<search>.+)$', search.search_parts, name='search-parts'),
    url('^search$', search.search, name='search'),

    url('^ajax/autocomplete$', search.search_autocomplete, name='search-autocomplete'),

    url('^add$', productions.production_add, name='production-add'),

    url('^profile/edit$', profiles.profile_edit, name='profile-edit'),
    url('^profile/(?P<username>.*)$', profiles.profile, name='profile'),
    url('^profile$', profiles.profile_user, name='profile-user'),

    url('^(?P<url>publicity)/feed$', NewsFeed()),
    url('^publicity$', news.NewsIndex.as_view(), name='news-index'),
    url('^publicity/(?P<year>\d{4})$', news.NewsYear.as_view(), name='news-year'),
    url('^publicity/(?P<year>\d{4})/(?P<month>\w+)$', news.NewsMonth.as_view(), name='news-month'),
    url('^publicity/(?P<year>\d{4})/(?P<month>\w+)/(?P<slug>[-\w]+)$',
        news.NewsArticle.as_view(), name='news-entry'),

    url('^random$', views.random_production, name='random'),
    #url('forums/forum/', include('forums.django-forum.forum.urls')),
    #url('forums/simple/', include('forums.django-simpleforum.forum.urls')),
    #url('forums/bb/', include('forums.djangobb.djangobb.urls')),
    #url('forums/counterpoint/', include('forums.counterpoint.counterpoint.urls')),

    url('^lp/day/', include('lp.urls')),
]

urlpatterns += staticfiles_urlpatterns()


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
