from django.test import TestCase

from theatricalia.tests import make_production

from .models import Play
from people.models import Person
from profiles.models import User
from merged.models import Redirect

class PlayUnitTest(TestCase):
    def setUp(self):
        self.play = Play.objects.create(title='Hamlet')

    def test_play_author_display(self):
        person1 = Person.objects.create(first_name=u'Principal', last_name=u'Author')
        person2 = Person.objects.create(first_name=u'Secondary', last_name=u'Author')
        person3 = Person.objects.create(first_name=u'Tertiary', last_name=u'Author')
        self.assertEqual('%s' % self.play, 'Hamlet')
        self.play.authors.add(person1)
        self.assertEqual('%s' % self.play, 'Hamlet, by Principal Author')
        self.play.authors.add(person2)
        self.assertEqual('%s' % self.play, 'Hamlet, by Principal Author and Secondary Author')
        self.play.authors.add(person3)
        self.assertEqual('%s' % self.play, 'Hamlet, by Principal Author, Secondary Author, and Tertiary Author')

class PlayTest(TestCase):
    def setUp(self):
        self.prod = make_production('Hamlet', 'A tragedy', [ 'Shakespeare Productions' ], [ { 'name': 'Stirchley Theatre', 'start': '2013-01-01', 'end': '2013-01-14' } ], [ { 'first': u'Matthew', 'last': u'Somerville', 'role': 'Laertes' } ])
        self.play_id = self.prod.play.id32

    def test_short_url(self):
        resp = self.client.get('/p/%s' % self.play_id)
        self.assertRedirects(resp, self.prod.play.get_absolute_url(), status_code=301)

    def test_redirect_merged(self):
        play_copy = Play.objects.create(title='Hamlet')
        copy_id = play_copy.id
        copy_id32 = play_copy.id32
        play_copy.delete()
        Redirect.objects.create(old_object_id=copy_id, new_object=self.prod.play)
        resp = self.client.get('/p/%s' % copy_id32)
        self.assertRedirects(resp, self.prod.play.get_absolute_url(), status_code=301)
        resp = self.client.get('/play/%s/whatever' % copy_id32)
        self.assertRedirects(resp, self.prod.play.get_absolute_url(), status_code=301)

    def test_redirect_slugs(self):
        User.objects.create_user('test', password='test')
        self.client.login(username='test', password='test')
        for subpage in ('future', 'past', 'edit'):
            resp = self.client.get('/play/%s/hamlet-2/%s' % (self.play_id, subpage), follow=True)
            self.assertRedirects(resp, '/play/%s/hamlet/%s' % (self.play_id, subpage), status_code=301)

    def test_play_listing(self):
        resp = self.client.get('/plays/h')
        self.assertContains(resp, 'Hamlet')
        resp = self.client.get('/plays/0')
        self.assertNotContains(resp, 'Hamlet')
        resp = self.client.get('/plays/*')
        self.assertNotContains(resp, 'Hamlet')

    def test_play_viewing(self):
        resp = self.client.get('/play/%s/hamlet-old-title' % self.play_id, follow=True)
        self.assertRedirects(resp, '/play/%s/hamlet' % self.play_id, status_code=301)
        self.assertContains(resp, 'Hamlet')
        self.assertContains(resp, 'Stirchley Theatre')
        self.assertContains(resp, 'January 2013')

    def test_past(self):
        resp = self.client.get('/play/%s/hamlet/past' % self.play_id)
        self.assertContains(resp, 'Hamlet')

    def test_play_cancel_editing(self):
        User.objects.create_user('test', password='test')
        self.client.login(username='test', password='test')

        resp = self.client.get('/play/%s/hamlet/edit' % self.play_id)
        self.assertContains(resp, 'Editing Hamlet')
        resp = self.client.post('/play/%s/hamlet/edit' % self.play_id, { 'disregard': 'Disregard' }, follow=True)
        self.assertRedirects(resp, '/play/%s/hamlet' % self.play_id)
        self.assertContains(resp, 'ignored any changes you made')

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
