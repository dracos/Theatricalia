import re
from calendar import timegm

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.syndication.views import Feed as DjangoFeed, FeedDoesNotExist
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.db.models import Count
from django.utils.http import http_date

from profiles.models import User
from people.models import Person
from plays.models import Play
from places.models import Place
from productions.models import Production
from shortcuts import check_url, UnmatchingSlugException
from productions.objshow import productions_past
from news.models import Article

# Subclass of Feed overwriting __call__ to support URL redirects
class Feed(DjangoFeed):
    def __call__(self, request, *args, **kwargs):
        try:
            obj = self.get_object(request, *args, **kwargs)
        except UnmatchingSlugException, e:
            return HttpResponseRedirect(e.args[0].get_absolute_url() + '/feed')
        except ObjectDoesNotExist:
            raise Http404('Feed object does not exist.')
        feedgen = self.get_feed(obj, request)
        response = HttpResponse(content_type=feedgen.content_type)
        if hasattr(self, 'item_pubdate') or hasattr(self, 'item_updateddate'):
            # if item_pubdate or item_updateddate is defined for the feed, set
            # header so as ConditionalGetMiddleware is able to send 304 NOT MODIFIED
            response['Last-Modified'] = http_date(
                timegm(feedgen.latest_post_date().utctimetuple()))
        feedgen.write(response, 'utf-8')
        return response

class NearbyFeed(Feed):
    def get_object(self, request, coord):
        m = re.match('\s*([-\d.]+)\s*,\s*([-\d.]+)\s*$', coord)
        if not m:
            raise ObjectDoesNotExist
        self.point = (lat, lon) = m.groups()
        places = Place.objects.around(float(lat), float(lon))
        return places

    def title(self):
        return 'Theatricalia: Productions around %s,%s' % self.point

    def link(self):
        return '/search?q=' + ','.join(self.point)

    def description(self):
        return 'The latest productions around %s,%s from Theatricalia' % self.point

    def items(self, places):
        return productions_past(places, 'places')[:20]

class PlaceFeed(Feed):
    def get_object(self, request, id, slug):
        try:
            place = check_url(Place, id, slug)
        except:
            raise ObjectDoesNotExist
        return place

    def title(self, obj):
        return 'Theatricalia: Productions at %s' % obj

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url()

    def description(self, obj):
        return 'The latest productions at %s from Theatricalia' % obj

    def items(self, obj):
        return obj.productions.order_by('-id')[:20]

class PersonFeed(Feed):
    def get_object(self, request, id, slug):
        person = check_url(Person, id, slug)
        return person

    def title(self, person):
        return 'Theatricalia: Productions with, or of a play by, %s' % person

    def link(self, person):
        if not person:
            raise FeedDoesNotExist
        return person.get_absolute_url()

    def description(self, person):
        return 'The latest productions with, or of a play by, %s from Theatricalia' % person

    def items(self, person):
        prod_with = person.productions.all().annotate(Count('parts'))
        prod_by = Production.objects.filter(play__authors=person).annotate(Count('parts'))
        productions = prod_with | prod_by
        return productions.order_by('-id')[:20]

class PlayFeed(Feed):
    def get_object(self, request, id, slug):
        play = check_url(Play, id, slug)
        return play

    def title(self, obj):
        return 'Theatricalia: Productions of %s' % obj

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url()

    def description(self, obj):
        return 'The latest productions of %s from Theatricalia' % obj

    def items(self, obj):
        return obj.productions.order_by('-id')[:20]

class UserSeenFeed(Feed):
    def get_object(self, request, user):
        profile = User.objects.get(username=user)
        return profile

    def title(self, obj):
        return 'Theatricalia: Productions seen by %s' % obj

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.profile.get_absolute_url()

    def description(self, obj):
        return 'The latest productions seen by %s from Theatricalia' % obj

    def items(self, user):
        return user.visit_set.order_by('-id')[:20]

class NewsFeed(Feed):
    title = 'Theatricalia: News articles'
    link = 'https://theatricalia.com/publicity'
    description = 'The latest news articles from Theatricalia'

    def items(self):
        return Article.objects.visible().order_by('-created')[:20]

