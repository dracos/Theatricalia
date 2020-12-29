from django.test import TestCase

from productions.models import Production, ProductionCompany
from plays.models import Play
from places.models import Place
from people.models import Person


def make_production(play, description, companies=[], places=[], people=[]):
    play, _ = Play.objects.get_or_create(title=play)
    production = Production.objects.create(play=play, description=description)
    for company in companies:
        company, _ = ProductionCompany.objects.get_or_create(name=company)
        production.production_companies_set.create(productioncompany=company)
    for data in places:
        place, _ = Place.objects.get_or_create(name=data['name'])
        production.place_set.create(place=place, start_date=data['start'], end_date=data['end'])
    for data in people:
        person, _ = Person.objects.get_or_create(first_name=data['first'], last_name=data['last'])
        production.part_set.create(person=person, role=data['role'])
    return production


class TheatricaliaTest(TestCase):
    def test_front_page(self):
        self.client.get('/')

    def test_random_page(self):
        resp = self.client.get('/random')
        self.assertRedirects(resp, '/')
        prod = make_production(
            'Hamlet',
            'A tragedy',
            ['Shakespeare Productions'],
            [{'name': 'Theatre', 'start': '2013-01-01', 'end': '2013-01-14'}]
        )
        resp = self.client.get('/random')
        self.assertRedirects(resp, '/play/%s/hamlet/production/%s' % (prod.play.id32, prod.id32))

    def test_static_pages(self):
        self.client.get('/moo')
        self.client.get('/colophon')
        self.client.get('/about')
        self.client.get('/assistance')
        self.client.get('/criticism')

    def test_lowercase_urls(self):
        resp = self.client.get('/PlAys')
        self.assertRedirects(resp, '/plays')

    def test_remove_slash_urls(self):
        resp = self.client.get('/plays/')
        self.assertRedirects(resp, '/plays', status_code=301)

    def test_user_flow(self):
        resp = self.client.post('/tickets/boxoffice', {
            'name': 'Test', 'unicorn': 'test@example.org', 'username': 'test', 'password': 'test'})
        self.assertContains(resp, 'You are now registered and logged in')
        resp = self.client.get('/tickets/returns')
        self.assertContains(resp, 'You are now signed out')
        resp = self.client.post('/tickets', {'username': 'test', 'password': 'test'}, follow=True)
        self.assertRedirects(resp, '/profile/test', status_code=302)


class ProductionTest(TestCase):
    def test_production_viewing(self):
        prod = make_production(
            'Hamlet',
            'A tragedy',
            ['Shakespeare Productions'],
            [{'name': 'Stirchley Theatre', 'start': '2013-01-01', 'end': '2013-01-14'}],
            [{'first': u'Matthew', 'last': u'Somerville', 'role': 'Laertes'}]
        )
        resp = self.client.get('/play/%s/hamlet/production/%s' % (prod.play.id32, prod.id32))
        self.assertContains(resp, 'Hamlet')
        self.assertContains(resp, 'January 2013')
        resp = self.client.get('/play/%s/hamlet/production/%sb' % (prod.play.id32, prod.id32))
        self.assertEqual(resp.status_code, 404)
