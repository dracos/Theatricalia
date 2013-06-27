from django.test import TestCase

from theatricalia.tests import make_production

from .models import Person
from profiles.models import User

class PersonTest(TestCase):
    def setUp(self):
        make_production('Hamlet', 'A tragedy', [ 'Shakespeare Productions' ], [ { 'name': 'Stirchley Theatre', 'start': '2013-01-01', 'end': '2013-01-14' } ], [ { 'first': u'Matthew', 'last': u'Somerville', 'role': 'Laertes' } ])

    def test_short_url(self):
        resp = self.client.get('/a/1')
        self.assertRedirects(resp, '/person/1/matthew-somerville', status_code=301)

    def test_place_listing(self):
        resp = self.client.get('/people/s')
        self.assertContains(resp, 'Matthew Somerville')

    def test_place_viewing(self):
        resp = self.client.get('/person/1/matthew', follow=True)
        self.assertRedirects(resp, '/person/1/matthew-somerville')
        self.assertContains(resp, 'Matthew Somerville')
        self.assertContains(resp, 'Hamlet')
        self.assertContains(resp, 'January 2013')

    def test_past(self):
        resp = self.client.get('/person/1/matthew-somerville/past')
        self.assertContains(resp, 'Hamlet')

    def test_place_editing(self):
        resp = self.client.get('/add?person=1')
        self.assertRedirects(resp, '/tickets?next=/add%3Fperson%3D1')

        User.objects.create_user('test', password='test')
        self.client.login(username='test', password='test')

        resp = self.client.get('/add?person=1')
        self.assertContains(resp, 'Adding production')
        # TODO Test submission here takes you to page with person's name already there

        resp = self.client.get('/person/1/matthew-somerville/edit')
        self.assertContains(resp, 'Editing Matthew Somerville')
        resp = self.client.post('/person/1/matthew-somerville/edit', {
            'first_name': 'Matthew',
            'last_name': 'Somerville',
            'bio': 'Bunnysitter',
            'dob': '19 September 1980',
            'web': 'http://dracos.co.uk/',
        }, follow=True)
        self.assertRedirects(resp, '/person/1/matthew-somerville')
        self.assertContains(resp, 'Your changes have been stored, thank you.')
        self.assertContains(resp, 'Bunnysitter')
        self.assertContains(resp, '19th September 1980')
        self.assertContains(resp, 'dracos.co.uk')
