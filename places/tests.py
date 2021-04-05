from django.test import TestCase

from theatricalia.tests import make_production
from profiles.models import User


class PlaceTest(TestCase):
    def setUp(self):
        prod = make_production(
            'Hamlet',
            'A tragedy',
            ['Shakespeare Productions'],
            [{'name': 'Stirchley Theatre', 'start': '2013-01-01', 'end': '2013-01-14'}],
            [{'first': u'Matthew', 'last': u'Somerville', 'role': 'Laertes'}]
        )
        self.place_id = prod.places.all()[0].id32

    def test_short_url(self):
        resp = self.client.get('/t/%s' % self.place_id)
        self.assertRedirects(resp, '/place/%s/stirchley-theatre' % self.place_id, status_code=301)

    def test_place_listing(self):
        resp = self.client.get('/places/s')
        self.assertContains(resp, 'Stirchley Theatre')

    def test_place_viewing(self):
        resp = self.client.get('/place/%s/kings-heath-theatre' % self.place_id, follow=True)
        self.assertRedirects(resp, '/place/%s/stirchley-theatre' % self.place_id, status_code=301)
        self.assertContains(resp, 'Hamlet')
        self.assertContains(resp, 'Stirchley Theatre')
        self.assertContains(resp, 'January 2013')

    def test_past(self):
        resp = self.client.get('/place/%s/stirchley-theatre/past' % self.place_id)
        self.assertContains(resp, 'Hamlet')
        self.assertContains(resp, 'January 2013')

    def test_place_editing(self):
        resp = self.client.get('/place/%s/stirchley-theatre/add' % self.place_id)
        self.assertRedirects(resp, '/tickets?next=/place/%s/stirchley-theatre/add' % self.place_id)

        User.objects.create_user('test', password='test')
        self.client.login(username='test', password='test')

        resp = self.client.get('/place/%s/stirchley-theatre/add' % self.place_id)
        self.assertContains(resp, 'Adding production')
        self.assertContains(resp, 'Stirchley Theatre')

        resp = self.client.get('/place/%s/stirchley-theatre/edit' % self.place_id)
        self.assertContains(resp, 'Editing Stirchley Theatre')
        resp = self.client.post('/place/%s/stirchley-theatre/edit' % self.place_id, {
            'name': 'Stirchley Theatre',
            'description': 'Performs in the Co-op car park',
            'location-0-town': 'Birmingham',
            'location-0-opening_date': 'May 2008',
            'name-TOTAL_FORMS': '1',
            'name-INITIAL_FORMS': '0',
            'location-TOTAL_FORMS': '1',
            'location-INITIAL_FORMS': '0',
        }, follow=True)
        self.assertRedirects(resp, '/place/%s/stirchley-theatre' % self.place_id)
        self.assertContains(resp, 'Your changes have been stored; thank you.')
        self.assertContains(resp, 'Performs in the Co-op car park')
        self.assertContains(resp, 'May 2008')
        self.assertContains(resp, 'Birmingham')
