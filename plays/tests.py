from django.test import TestCase

from theatricalia.tests import make_production

from .models import Play
from profiles.models import User

class PlayTest(TestCase):
    def setUp(self):
        self.prod = make_production('Hamlet', 'A tragedy', [ 'Shakespeare Productions' ], [ { 'name': 'Stirchley Theatre', 'start': '2013-01-01', 'end': '2013-01-14' } ], [ { 'first': u'Matthew', 'last': u'Somerville', 'role': 'Laertes' } ])
        self.play_id = self.prod.play.id32

    def test_short_url(self):
        resp = self.client.get('/p/%s' % self.play_id)
        self.assertRedirects(resp, self.prod.play.get_absolute_url(), status_code=301)

    def test_play_listing(self):
        resp = self.client.get('/plays/h')
        self.assertContains(resp, 'Hamlet')

    def test_play_viewing(self):
        resp = self.client.get('/play/%s/hamlet-old-title' % self.play_id, follow=True)
        self.assertRedirects(resp, '/play/%s/hamlet' % self.play_id, status_code=301)
        self.assertContains(resp, 'Hamlet')
        self.assertContains(resp, 'Stirchley Theatre')
        self.assertContains(resp, 'January 2013')

    def test_past(self):
        resp = self.client.get('/play/%s/hamlet/past' % self.play_id)
        self.assertContains(resp, 'Hamlet')

    def test_play_editing(self):
        resp = self.client.get('/play/%s/hamlet/add' % self.play_id)
        self.assertRedirects(resp, '/tickets?next=/play/%s/hamlet/add' % self.play_id)

        User.objects.create_user('test', password='test')
        self.client.login(username='test', password='test')

        resp = self.client.get('/play/%s/hamlet/add' % self.play_id)
        self.assertContains(resp, 'Adding production')
        self.assertContains(resp, 'Hamlet')

        resp = self.client.get('/play/%s/hamlet/edit' % self.play_id)
        self.assertContains(resp, 'Editing Hamlet')
        resp = self.client.post('/play/%s/hamlet/edit' % self.play_id, {
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

        person_id = self.prod.parts.all()[0].id

        resp = self.client.post('/play/%s/hamlet/edit' % self.play_id, {
            'title': 'Hamlet',
            'description': 'Tragedy',
            'authors': '[]',
            'form-TOTAL_FORMS': 2,
            'form-INITIAL_FORMS': 0,
            'form-0-person_choice': 'new',
            'form-0-person': 'William Shakespeare',
            'form-1-person_choice': person_id,
            'form-1-person': 'Matthew Somerville',
        }, follow=True)
        self.assertRedirects(resp, '/play/%s/hamlet' % self.play_id)
        self.assertContains(resp, 'Tragedy')
        self.assertContains(resp, 'Your changes have been stored; thank you.')
        self.assertContains(resp, 'William Shakespeare')
        self.assertContains(resp, 'Matthew Somerville')
