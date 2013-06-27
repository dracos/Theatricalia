from django.test import TestCase

from theatricalia.tests import make_production

from .models import Play
from profiles.models import User

class PlayTest(TestCase):
    def setUp(self):
        make_production('Hamlet', 'A tragedy', [ 'Shakespeare Productions' ], [ { 'name': 'Stirchley Theatre', 'start': '2013-01-01', 'end': '2013-01-14' } ], [ { 'first': u'Matthew', 'last': u'Somerville', 'role': 'Laertes' } ])

    def test_short_url(self):
        resp = self.client.get('/p/1')
        self.assertRedirects(resp, '/play/1/hamlet', status_code=301)

    def test_play_listing(self):
        resp = self.client.get('/plays/h')
        self.assertContains(resp, 'Hamlet')

    def test_play_viewing(self):
        resp = self.client.get('/play/1/hamlet-old-title', follow=True)
        self.assertRedirects(resp, '/play/1/hamlet')
        self.assertContains(resp, 'Hamlet')
        self.assertContains(resp, 'Stirchley Theatre')
        self.assertContains(resp, 'January 2013')

    def test_past(self):
        resp = self.client.get('/play/1/hamlet/past')
        self.assertContains(resp, 'Hamlet')

    def test_play_editing(self):
        resp = self.client.get('/play/1/hamlet/add')
        self.assertRedirects(resp, '/tickets?next=/play/1/hamlet/add')

        User.objects.create_user('test', password='test')
        self.client.login(username='test', password='test')

        resp = self.client.get('/play/1/hamlet/add')
        self.assertContains(resp, 'Adding production')
        self.assertContains(resp, 'Hamlet')

        resp = self.client.get('/play/1/hamlet/edit')
        self.assertContains(resp, 'Editing Hamlet')
        resp = self.client.post('/play/1/hamlet/edit', {
            'title': 'Hamlet',
            'description': 'Tragedy',
            'authors': '[]',
            'form-TOTAL_FORMS': 2,
            'form-INITIAL_FORMS': 0,
            'form-0-person': 'William Shakespeare',
            'form-1-person': 'Matthew Somerville',
        })
        self.assertContains(resp, 'Tragedy')
        self.assertContains(resp, 'last in Shakespeare Productions production of Hamlet, Stirchley Theatre')
        self.assertContains(resp, 'Laertes')
        self.assertContains(resp, 'A new person also called &lsquo;Matthew Somerville&rsquo;')

        resp = self.client.post('/play/1/hamlet/edit', {
            'title': 'Hamlet',
            'description': 'Tragedy',
            'authors': '[]',
            'form-TOTAL_FORMS': 2,
            'form-INITIAL_FORMS': 0,
            'form-0-person_choice': 'new',
            'form-0-person': 'William Shakespeare',
            'form-1-person_choice': '1',
            'form-1-person': 'Matthew Somerville',
        }, follow=True)
        self.assertRedirects(resp, '/play/1/hamlet')
        self.assertContains(resp, 'Tragedy')
        self.assertContains(resp, 'Your changes have been stored; thank you.')
        self.assertContains(resp, 'William Shakespeare')
        self.assertContains(resp, 'Matthew Somerville')
