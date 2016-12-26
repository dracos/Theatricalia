from django.test import TestCase

from theatricalia.tests import make_production

class SearchTest(TestCase):
    def setUp(self):
        prod = make_production('Hamlet', 'A tragedy', [ 'Shakespeare Productions' ], [ { 'name': 'Stirchley Theatre', 'start': '2013-01-01', 'end': '2013-01-14' } ], [ { 'first': u'Matthew', 'last': u'Somerville', 'role': 'Laertes' } ])
        self.place_id = prod.places.all()[0].id32
        make_production('Hamlet', 'Another tragedy', [ 'Shakespeare Productions' ], [ { 'name': 'Bournville Theatre', 'start': '2013-02-01', 'end': '2013-02-14' } ], [ { 'first': u'Matthew', 'last': u'Boulton', 'role': 'Hamlet' } ])

    def test_basic_search(self):
        resp = self.client.get('/search?q=hamlet')
        self.assertContains(resp, 'Hamlet')
        resp = self.client.get('/search?q=matthew')
        self.assertContains(resp, 'Matthew')
        resp = self.client.get('/search?q=mathew')
        self.assertContains(resp, 'Matthew')
        resp = self.client.get('/search?q=stirchley')
        self.assertRedirects(resp, '/place/%s/stirchley-theatre' % self.place_id)
        resp = self.client.get('/search?person=somerville&place=stirchley')
        self.assertContains(resp, 'Matthew')

