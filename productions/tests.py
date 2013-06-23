from django.test import TestCase

from .models import Production
from profiles.models import User

def play_form_defaults():
    return {
        'company-TOTAL_FORMS': '1',
        'company-INITIAL_FORMS': '0',
        'company-0-productioncompany_0': 'Mars Company',
        'description': 'A production set on Mars.',
        'place-TOTAL_FORMS': '1',
        'place-INITIAL_FORMS': '0',
        'place-0-place_0': 'Royal Birmingham Theatre',
        'place-0-start_date': '1st January 2004',
        'place-0-end_date': '10th January 2004',
    }

def play_form(kw):
    return dict(play_form_defaults(), **kw)

class ProductionTest(TestCase):
    def test_adding_production(self):
        # Not logged in
        resp = self.client.get('/add')
        self.assertRedirects(resp, '/tickets?next=/add')

        User.objects.create_user('test', password='test')
        self.client.login(username='test', password='test')

        resp = self.client.get('/add')
        self.assertContains(resp, 'Adding production')

        # New play
        resp = self.client.post('/add', play_form({ 'play_0': 'Hamlet' }))
        self.assertContains(resp, 'Please select one of the choices below:')
        self.assertContains(resp, 'A new play called &lsquo;Hamlet&rsquo;')
        resp = self.client.post('/add', play_form({ 'play_choice': 'new', 'play_0': 'Hamlet' }), follow=True)
        self.assertRedirects(resp, '/play/1/hamlet/production/1/edit/cast')
        self.assertContains(resp, 'Editing production')
        self.assertContains(resp, 'Your addition has been stored; thank you.')
        self.assertContains(resp, 'Add new Part')

        # Add a new person
        resp = self.client.post('/play/1/hamlet/production/1/edit/cast', {
            'person': 'Matthew',
            'production': 1,
            'role': 'Director',
            'cast': '3', # Crew
        }, follow=True)
        self.assertRedirects(resp, '/play/1/hamlet/production/1/edit/cast')
        self.assertContains(resp, 'Your new part has been added; thank you.')
        self.assertContains(resp, 'Matthew, Director <small>(Crew)</small>')

        # Check front end display
        production = Production.objects.get(id=1)
        resp = self.client.get('/play/1/hamlet/production/1')
        self.assertEqual(resp.context['production'], production)
        self.assertListEqual(list(resp.context['crew']), list(production.part_set.filter(cast=False)))

        # Edit it - need to hook up some mechanize thing
        resp = self.client.get('/play/1/hamlet/production/1/edit')
        resp = self.client.post('/play/1/hamlet/production/1/edit', {
            'play_0': 'Hamlet', 'play_1': '1', # Keep existing
            'description': 'New description',
            'company-TOTAL_FORMS': '2', 'company-INITIAL_FORMS': '1',
            'company-0-productioncompany_0': 'Mars Company', 'company-0-productioncompany_1': '1', 'company-0-id': '1',
            'place-TOTAL_FORMS': '2', 'place-INITIAL_FORMS': '1',
            'place-0-place_0': 'Royal Birmingham Theatre', 'place-0-place_1': '1', 'place-0-id': '1',
            'place-0-start_date': '1st January 2004', 'place-0-end_date': '10th January 2004',
        }, follow=True)
        self.assertRedirects(resp, '/play/1/hamlet/production/1')
        self.assertContains(resp, 'Your changes have been stored; thank you.')
        self.assertContains(resp, 'New description')

        # Now try adding with the existing play etc.
        resp = self.client.get('/add')
        self.assertContains(resp, 'Adding production')

        # If autocomplete used
        resp = self.client.post('/add', play_form({ 'play_0': 'Hamlet', 'play_1': '1' }), follow=True)
        self.assertRedirects(resp, '/play/1/hamlet/production/2/edit/cast')
        self.assertContains(resp, 'Editing production')
        self.assertContains(resp, 'Your addition has been stored; thank you.')
        self.assertContains(resp, 'Add new Part')

        # Similar title checking
        resp = self.client.post('/add', play_form({ 'play_0': 'Ham' }))
        self.assertContains(resp, 'Please select one of the choices below:')
        self.assertContains(resp, 'Hamlet')
        self.assertContains(resp, 'A new play called &lsquo;Ham&rsquo;');
        resp = self.client.post('/add', play_form({ 'play_choice': '1', 'play_0': 'Ham' }), follow=True)
        self.assertRedirects(resp, '/play/1/hamlet/production/3/edit/cast')
        self.assertContains(resp, 'Editing production')
        self.assertContains(resp, 'Your addition has been stored; thank you.')
        self.assertContains(resp, 'Add new Part')

        # Add an existing person
        resp = self.client.post('/play/1/hamlet/production/3/edit/cast', {
            'person': 'Matthew',
            'production': 3,
            'role': 'Director',
            'cast': '3', # Crew
        })
        self.assertContains(resp, '/person/1/matthew')
        self.assertContains(resp, 'A new person also called &lsquo;Matthew&rsquo;')
        resp = self.client.post('/play/1/hamlet/production/3/edit/cast', {
            'person_choice': 'new',
            'person': 'Matthew',
            'production': 3,
            'role': 'Director',
            'cast': '3', # Crew
        }, follow=True)
        self.assertRedirects(resp, '/play/1/hamlet/production/3/edit/cast')
        self.assertContains(resp, 'Your new part has been added; thank you.')
        self.assertContains(resp, 'Matthew, Director <small>(Crew)</small>')

