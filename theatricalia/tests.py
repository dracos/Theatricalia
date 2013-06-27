from django.test import TestCase

from productions.models import Production, ProductionCompany
from plays.models import Play
from places.models import Place
from people.models import Person

def make_production(play, description, companies=[], places=[], people=[]):
    play, _ = Play.objects.get_or_create( title=play )
    production = Production.objects.create( play=play, description=description )
    for company in companies:
        company, _ = ProductionCompany.objects.get_or_create( name=company )
        production.production_companies_set.create( productioncompany=company )
    for data in places:
        place, _ = Place.objects.get_or_create( name=data['name'] )
        production.place_set.create( place=place, start_date=data['start'], end_date=data['end'] )
    for data in people:
        person, _ = Person.objects.get_or_create( first_name=data['first'], last_name=data['last'] )
        production.part_set.create( person=person, role=data['role'] )
    return production

class TheatricaliaTest(TestCase):
    def test_front_page(self):
        resp = self.client.get('/')

    def test_random_page(self):
        resp = self.client.get('/random')
        self.assertRedirects(resp, '/')
        make_production('Hamlet', 'A tragedy', [ 'Shakespeare Productions' ], [ { 'name': 'Theatre', 'start': '2013-01-01', 'end': '2013-01-14' } ])
        resp = self.client.get('/random')
        self.assertRedirects(resp, '/play/1/hamlet/production/1')

    def test_static_pages(self):
        resp = self.client.get('/moo')
        resp = self.client.get('/colophon')
        resp = self.client.get('/about')
        resp = self.client.get('/assistance')
        resp = self.client.get('/criticism')

    def test_lowercase_urls(self):
        resp = self.client.get('/PlAys')
        self.assertRedirects(resp, '/plays')

    def test_remove_slash_urls(self):
        resp = self.client.get('/plays/')
        self.assertRedirects(resp, '/plays', status_code=301)

class ProductionTest(TestCase):
    def test_production_viewing(self):
        make_production('Hamlet', 'A tragedy', [ 'Shakespeare Productions' ], [ { 'name': 'Stirchley Theatre', 'start': '2013-01-01', 'end': '2013-01-14' } ], [ { 'first': u'Matthew', 'last': u'Somerville', 'role': 'Laertes' } ])
        resp = self.client.get('/play/1/hamlet/production/1')
        self.assertContains(resp, 'Hamlet')
        self.assertContains(resp, 'January 2013')
        resp = self.client.get('/play/1/hamlet/production/2')
        self.assertEqual(resp.status_code, 404)
