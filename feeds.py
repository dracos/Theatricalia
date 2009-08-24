import re
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.syndication.feeds import Feed
from people.models import Person
from plays.models import Play
from places.models import Place
from shortcuts import check_url
from productions.objshow import productions_past

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
        place = check_url(Place, bits[0], bits[1])
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

    def title(self, obj):
        return 'Theatricalia: Productions with %s' % obj

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url()

    def description(self, obj):
        return 'The latest productions with %s from Theatricalia' % obj

    def items(self, obj):
        return obj.productions.order_by('-id').distinct()[:20]

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


