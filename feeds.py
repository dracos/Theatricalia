import re

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.syndication.views import Feed, FeedDoesNotExist
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.db.models import Count

from profiles.models import User
from people.models import Person
from plays.models import Play
from places.models import Place
from productions.models import Production
from shortcuts import check_url, UnmatchingSlugException
from productions.objshow import productions_past
from news.models import Article

# Copy of django.contrib.syndication.views.feed changed to support URL redirects
def view(request, url, feed_dict):
    if not feed_dict:
        raise Http404, "No feeds are registered."

    try:
        slug, param = url.split('/', 1)
    except ValueError:
        slug, param = url, ''

    try:
        f = feed_dict[slug]
    except KeyError:
        raise Http404, "Slug %r isn't registered." % slug

    try:
        feedgen = f(slug, request).get_feed(param)
    except UnmatchingSlugException, e:
        return HttpResponseRedirect(e.args[0].get_absolute_url() + '/feed')
    except FeedDoesNotExist:
        raise Http404, "Invalid feed parameters. Slug %r is valid, but other parameters, or lack thereof, are not." % slug

    response = HttpResponse(mimetype=feedgen.mime_type)
    feedgen.write(response, 'utf-8')
    return response

class NearbyFeed(Feed):
    def get_object(self, bits):
        if len(bits) != 1:
            raise ObjectDoesNotExist
        m = re.match('\s*([-\d.]+)\s*,\s*([-\d.]+)\s*$', bits[0])
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
    def get_object(self, bits):
        if len(bits) != 2:
            raise ObjectDoesNotExist
        try:
            place = check_url(Place, bits[0], bits[1])
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
    def get_object(self, bits):
        if len(bits) != 2:
            raise ObjectDoesNotExist
        person = check_url(Person, bits[0], bits[1])
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
    def get_object(self, bits):
        if len(bits) != 2:
            raise ObjectDoesNotExist
        play = check_url(Play, bits[0], bits[1])
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
    def get_object(self, bits):
        if len(bits) != 1:
            raise ObjectDoesNotExist
        profile = User.objects.get(username=bits[0])
        return profile

    def title(self, obj):
        return 'Theatricalia: Productions seen by %s' % obj

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url().lower()

    def description(self, obj):
        return 'The latest productions seen by %s from Theatricalia' % obj

    def items(self, user):
        return user.visit_set.order_by('-id')[:20]

class NewsFeed(Feed):
    title = 'Theatricalia: News articles'
    link = 'http://theatricalia.com/publicity'
    description = 'The latest news articles from Theatricalia'

    def items(self):
        return Article.objects.visible().order_by('-created')[:20]

