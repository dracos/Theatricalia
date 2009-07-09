from django.contrib.syndication.feeds import Feed
from people.models import Person
from plays.models import Play
from places.models import Place

class PlaceFeed(Feed):
	def get_object(self, bits):
		if len(bits) != 1:
			raise ObjectDoesNotExist
		return Place.objects.get(slug=bits[0])

	def title(self, obj):
		return 'Theatricalia: Productions at %s' % obj

	def link(self, obj):
		if not obj:
			raise FeedDoesNotExist
		return obj.get_absolute_url()

	def description(self, obj):
		return 'The latest productions at %s from Theatricalia' % obj

	def items(self, obj):
		return obj.productions.order_by('-end_date')[:20]

class PersonFeed(Feed):
	def get_object(self, bits):
		if len(bits) != 1:
			raise ObjectDoesNotExist
		return Person.objects.get(slug=bits[0])

	def title(self, obj):
		return 'Theatricalia: Productions with %s' % obj

	def link(self, obj):
		if not obj:
			raise FeedDoesNotExist
		return obj.get_absolute_url()

	def description(self, obj):
		return 'The latest productions with %s from Theatricalia' % obj

	def items(self, obj):
		return obj.productions.order_by('-end_date').distinct()[:20]

class PlayFeed(Feed):
	def get_object(self, bits):
		if len(bits) != 1:
			raise ObjectDoesNotExist
		return Play.objects.get(slug=bits[0])

	def title(self, obj):
		return 'Theatricalia: Productions of %s' % obj

	def link(self, obj):
		if not obj:
			raise FeedDoesNotExist
		return obj.get_absolute_url()

	def description(self, obj):
		return 'The latest productions of %s from Theatricalia' % obj

	def items(self, obj):
		return obj.productions.order_by('-end_date')[:20]


