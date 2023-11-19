from django.conf import settings

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path, register_converter

from . import views

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

from django.contrib import admin
from django.contrib.auth import views as auth_views

from feeds import PersonFeed, PlayFeed, PlaceFeed, NearbyFeed, UserSeenFeed, NewsFeed


class StringConverter:
    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


class Base32Converter(StringConverter):
    regex = '[0-9a-zA-Z]+'


class LetterConverter(StringConverter):
    regex = '[a-z0*]'


register_converter(Base32Converter, 'b32')
register_converter(LetterConverter, 'letter')

urlpatterns = [
    # Example:
    # (r'^theatricalia/', include('theatricalia.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    path('admin/', admin.site.urls),

    path('tickets/boxoffice', profiles.register, name='register'),
    path('tickets/<b32:uidb32>-<path:token>', profiles.register_confirm, name='register-confirm'),
    path('tickets', profiles.LoginView.as_view(), name='login'),
    path('tickets/exchange', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('tickets/exchanged', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('tickets/lost', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('tickets/lost/done', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('tickets/lost/<slug:uidb64>/<path:token>', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('tickets/lost/found', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('tickets/returns', auth_views.LogoutView.as_view(), name='logout'),

    path('', views.home, name='home'),

    path('about', views.static_about, name='about'),
    path('assistance', views.static_help, name='help'),
    path('criticism', views.static_contact, name='criticism'),
    path('colophon', views.static_colophon, name='colophon'),
    path('moo', views.static_moocards, name='moo'),

    path('play/<b32:id>/<slug:slug>/feed', PlayFeed()),
    path('person/<b32:id>/<slug:slug>/feed', PersonFeed()),
    path('place/<b32:id>/<slug:slug>/feed', PlaceFeed()),
    path('around/<slug:coord>/feed', NearbyFeed()),
    path('profile/<slug:user>/feed/seen', UserSeenFeed()),

    re_path('^play/.*?/(?P<url>production/.*/merge)$', merged.merge),
    re_path('^(?P<url>(play|person|place|company)/.*)/merge$', merged.merge),

    path('d/<b32:production_id>', productions.production_short_url),
    path('production/<b32:production_id>', productions.production_short_url),
    path('c/<b32:company_id>', productions.production_company_short_url),
    path('p/<b32:play_id>', plays.play_short_url),
    path('t/<b32:place_id>', places.place_short_url),
    path('a/<b32:person_id>', people.person_short_url),

    re_path('^api/(?P<type>production|play|place|company|person)/(?P<id>[^/]+)/flickr$', common.api_flickr),

    path('plays', plays.PlayList.as_view(), name='plays_all'),
    path('plays/<letter:letter>', plays.PlayList.as_view(), name='plays'),
    re_path('^play/(?P<play_id>.*?)/(?P<play>.*?)/production/(?P<production_id>[0-9a-z]+)/seen/(?P<type>add|remove)$', productions.production_seen, name='production-seen'),
    path('play/<b32:play_id>/<slug:play>/production/<b32:production_id>/edit', productions.production_edit, name='production-edit'),
    path('play/<b32:play_id>/<slug:play>/production/<b32:production_id>/edit/cast', productions.production_edit_cast, name='production-edit-cast'),
    path('play/<b32:play_id>/<slug:play>/production/<b32:production_id>/edit/<int:part_id>', productions.part_edit, name='part-edit'),
    path('play/<b32:play_id>/<slug:play>/production/<b32:production_id>/corrected', productions.production_corrected, name='production-corrected'),
    re_path(r'^play/(?P<play_id>.*?)/(?P<play>.*?)/production/(?P<production_id>[0-9a-z]+)\.(?P<format>json)$', productions.production, name='production-json'),
    path('play/<b32:play_id>/<slug:play>/production/<b32:production_id>', productions.production, name='production'),
    path('play/<b32:play_id>/<slug:play>/future', plays.play_productions, {'type': 'future'}, name='play-productions-future'),
    path('play/<b32:play_id>/<slug:play>/past', plays.play_productions, {'type': 'past'}, name='play-productions-past'),
    path('play/<b32:play_id>/<slug:play>/edit', plays.play_edit, name='play-edit'),
    path('play/<b32:play_id>/<slug:play>/add', productions.add_from_play, name='play-production-add'),
    path('play/<b32:play_id>/<slug:play>', plays.play, name='play'),
    path('play/<b32:play_id>', plays.play_short_url),

    # url('^play/(?P<play>.*?)/part/(?P<part>.*)$', productions.by_part),

    path('people', people.PersonList.as_view(), name='people_all'),
    path('people/<letter:letter>', people.PersonList.as_view(), name='people'),
    re_path('^person/(?P<person_id>.*?)/(?P<person>.*)/future$', people.person_productions, {'type': 'future'}, name='person-productions-future'),
    re_path('^person/(?P<person_id>.*?)/(?P<person>.*)/past$', people.person_productions, {'type': 'past'}, name='person-productions-past'),
    re_path('^person/(?P<person_id>.*?)/(?P<person>.*)/edit$', people.person_edit, name='person-edit'),
    re_path(r'^person/(?P<person_id>.*?)/(?P<person>.*)\.js$', people.person_js, name='person-json'),
    re_path('^person/(?P<person_id>.*?)/(?P<person>.*)$', people.person, name='person'),
    re_path('^person/(?P<person_id>.+)$', people.person_short_url),

    path('places', places.PlaceList.as_view(), name='places_all'),
    path('places/<letter:letter>', places.PlaceList.as_view(), name='places'),
    re_path('^place/(?P<place_id>[^/]+)/(?P<place>.*)/future$', places.place_productions, {'type': 'future'}, name='place-productions-future'),
    re_path('^place/(?P<place_id>[^/]+)/(?P<place>.*)/past$', places.place_productions, {'type': 'past'}, name='place-productions-past'),
    re_path('^place/(?P<place_id>[^/]+)/(?P<place>.*)/edit$', places.place_edit, name='place-edit'),
    re_path('^place/(?P<place_id>[^/]+)/(?P<place>.*)/add$', productions.add_from_place, name='place-production-add'),
    re_path('^place/(?P<place_id>[^/]+)/(?P<place>.*)/productions$', places.productions, name='place-productions'),
    path('place/<b32:place_id>/<slug:place>/people', places.people, name='place-people'),
    path('place/<b32:place_id>/<slug:place>', places.place, name='place'),
    path('place/<b32:place_id>', places.place_short_url),

    re_path('^company/(?P<company_id>[^/]+)/(?P<company>.*)/future$', productions.company_productions, {'type': 'future'}, name='company-productions-future'),
    re_path('^company/(?P<company_id>[^/]+)/(?P<company>.*)/past$', productions.company_productions, {'type': 'past'}, name='company-productions-past'),
    re_path('^company/(?P<company_id>[^/]+)/(?P<company>.*)/edit$', productions.company_edit, name='company-edit'),
    re_path('^company/(?P<company_id>[^/]+)/(?P<company>.*)/add$', productions.add_from_company, name='company-production-add'),
    re_path('^company/(?P<company_id>[^/]+)/(?P<company>[^/]*)$', productions.company, name='company'),
    re_path('^company/(?P<company_id>[^/]+)$', productions.production_company_short_url),

    path('observations/post/', productions.post_comment_wrapper),
    re_path(r'^observations/remove/(?P<comment_id>\d+)', productions.hide_comment, name='hide-comment'),
    path('observations/', include('django_comments.urls')),
    path('photograph/take/', photos.take_photo, name='take-photo'),
    path('photograph/taken/', photos.photo_taken, name='photo-taken'),
    re_path('^photograph/view/(?P<photo_id>[0-9a-z]+)$', photos.view, name='photo-view'),

    re_path('^search/around/(?P<s>.+)/future$', search.search_around, {'type': 'future'}, name='search-around-future'),
    re_path('^search/around/(?P<s>.+)/past$', search.search_around, {'type': 'past'}, name='search-around-past'),
    re_path('^search/around/(?P<s>.+)$', search.search_around, name='search-around'),
    re_path('^search/parts/(?P<search>.+)$', search.search_parts, name='search-parts'),
    path('search', search.search, name='search'),

    path('ajax/autocomplete', search.search_autocomplete, name='search-autocomplete'),

    path('add', productions.production_add, name='production-add'),

    path('profile/edit', profiles.profile_edit, name='profile-edit'),
    path('profile/<slug:username>', profiles.profile, name='profile'),
    path('profile', profiles.profile_user, name='profile-user'),

    path('publicity/feed', NewsFeed()),
    path('publicity', news.NewsIndex.as_view(), name='news-index'),
    path('publicity/<int:year>', news.NewsYear.as_view(), name='news-year'),
    path('publicity/<int:year>/<slug:month>', news.NewsMonth.as_view(), name='news-month'),
    path('publicity/<int:year>/<slug:month>/<slug:slug>',
         news.NewsArticle.as_view(), name='news-entry'),

    path('random', views.random_production, name='random'),
    # url('forums/forum/', include('forums.django-forum.forum.urls')),
    # url('forums/simple/', include('forums.django-simpleforum.forum.urls')),
    # url('forums/bb/', include('forums.djangobb.djangobb.urls')),
    # url('forums/counterpoint/', include('forums.counterpoint.counterpoint.urls')),

    path('lp/day/', include('lp.urls')),
]

urlpatterns += staticfiles_urlpatterns()


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
