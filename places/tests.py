from django.test import TestCase

from theatricalia.tests import make_production

from .models import Place
from profiles.models import User

class PlaceTest(TestCase):
    def setUp(self):
        make_production('Hamlet', 'A tragedy', [ 'Shakespeare Productions' ], [ { 'name': 'Stirchley Theatre', 'start': '2013-01-01', 'end': '2013-01-14' } ], [ { 'first': u'Matthew', 'last': u'Somerville', 'role': 'Laertes' } ])

    def test_short_url(self):
        resp = self.client.get('/t/1')
        self.assertRedirects(resp, '/place/1/stirchley-theatre', status_code=301)

    def test_place_listing(self):
        resp = self.client.get('/places/s')
        self.assertContains(resp, 'Stirchley Theatre')

    def test_place_viewing(self):
        resp = self.client.get('/place/1/kings-heath-theatre', follow=True)
        self.assertRedirects(resp, '/place/1/stirchley-theatre', status_code=301)
        self.assertContains(resp, 'Hamlet')
        self.assertContains(resp, 'Stirchley Theatre')
        self.assertContains(resp, 'January 2013')

    def test_past(self):
        resp = self.client.get('/place/1/stirchley-theatre/past')
        self.assertContains(resp, 'Hamlet')
        self.assertContains(resp, 'January 2013')

    def test_place_editing(self):
        resp = self.client.get('/place/1/stirchley-theatre/add')
        self.assertRedirects(resp, '/tickets?next=/place/1/stirchley-theatre/add')

        User.objects.create_user('test', password='test')
        self.client.login(username='test', password='test')

        resp = self.client.get('/place/1/stirchley-theatre/add')
        self.assertContains(resp, 'Adding production')
        self.assertContains(resp, 'Stirchley Theatre')

        resp = self.client.get('/place/1/stirchley-theatre/edit')
        self.assertContains(resp, 'Editing Stirchley Theatre')
        resp = self.client.post('/place/1/stirchley-theatre/edit', {
            'name': 'Stirchley Theatre',
            'description': 'Performs in the Co-op car park',
            'town': 'Birmingham',
            'opening_date': 'May 2008',
        }, follow=True)
        self.assertRedirects(resp, '/place/1/stirchley-theatre-birmingham')
        self.assertContains(resp, 'Your changes have been stored; thank you.')
        self.assertContains(resp, 'Performs in the Co-op car park')
        self.assertContains(resp, 'May 2008')
        self.assertContains(resp, 'Birmingham')
