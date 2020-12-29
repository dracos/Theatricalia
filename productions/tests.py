from django.test import TestCase

from .models import Production
from profiles.models import User

from theatricalia.tests import make_production


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
        resp = self.client.post('/add', play_form({'play_0': 'Hamlet'}))
        self.assertContains(resp, 'Please select one of the choices below:')
        self.assertContains(resp, 'A new play called &lsquo;Hamlet&rsquo;')
        resp = self.client.post('/add', play_form({'play_choice': 'new', 'play_0': 'Hamlet'}), follow=True)

        prod = Production.objects.order_by('-id')[0]
        self.assertRedirects(resp, '/play/%s/hamlet/production/%s/edit/cast' % (prod.play.id32, prod.id32))
        self.assertContains(resp, 'Editing production')
        self.assertContains(resp, 'Your addition has been stored; thank you.')
        self.assertContains(resp, 'Add new Part')

        # Add a new person
        resp = self.client.post('/play/%s/hamlet/production/%s/edit/cast' % (prod.play.id32, prod.id32), {
            'person': 'Matthew',
            'production': prod.id,
            'role': 'Director',
            'cast': '3',  # Crew
        }, follow=True)
        self.assertRedirects(resp, '/play/%s/hamlet/production/%s/edit/cast' % (prod.play.id32, prod.id32))
        self.assertContains(resp, 'Your new part has been added; thank you.')
        self.assertContains(resp, 'Matthew, Director <small>(Crew)</small>')

        # Check front end display
        production = prod
        resp = self.client.get('/play/%s/hamlet/production/%s' % (prod.play.id32, prod.id32))
        self.assertEqual(resp.context['production'], production)
        self.assertListEqual(list(resp.context['crew']), list(production.part_set.filter(cast=False)))

        # Edit it - need to hook up some mechanize thing
        resp = self.client.get('/play/%s/hamlet/production/%s/edit' % (prod.play.id32, prod.id32))
        resp = self.client.post('/play/%s/hamlet/production/%s/edit' % (prod.play.id32, prod.id32), {
            'play_0': 'Hamlet', 'play_1': prod.play.id,  # Keep existing
            'description': 'New description',
            'company-TOTAL_FORMS': '2', 'company-INITIAL_FORMS': '1',
            'company-0-productioncompany_0': 'Mars Company',
            'company-0-productioncompany_1': prod.companies.all()[0].id,
            'company-0-id': prod.production_companies_set.all()[0].id,
            'place-TOTAL_FORMS': '2', 'place-INITIAL_FORMS': '1',
            'place-0-place_0': 'Royal Birmingham Theatre',
            'place-0-place_1': prod.places.all()[0].id,
            'place-0-id': prod.place_set.all()[0].id,
            'place-0-start_date': '1st January 2004', 'place-0-end_date': '10th January 2004',
        }, follow=True)
        self.assertRedirects(resp, '/play/%s/hamlet/production/%s' % (prod.play.id32, prod.id32))
        self.assertContains(resp, 'Your changes have been stored; thank you.')
        self.assertContains(resp, 'New description')

        # Now try adding with the existing play etc.
        resp = self.client.get('/add')
        self.assertContains(resp, 'Adding production')

        # If autocomplete used
        resp = self.client.post('/add', play_form({'play_0': 'Hamlet', 'play_1': prod.play.id}), follow=True)
        prod2 = Production.objects.order_by('-id')[0]
        self.assertRedirects(resp, '/play/%s/hamlet/production/%s/edit/cast' % (prod2.play.id32, prod2.id32))
        self.assertContains(resp, 'Editing production')
        self.assertContains(resp, 'Your addition has been stored; thank you.')
        self.assertContains(resp, 'Add new Part')

        # Similar title checking
        resp = self.client.post('/add', play_form({'play_0': 'Ham'}))
        self.assertContains(resp, 'Please select one of the choices below:')
        self.assertContains(resp, 'Hamlet')
        self.assertContains(resp, 'A new play called &lsquo;Ham&rsquo;')
        resp = self.client.post('/add', play_form({'play_choice': prod.play.id, 'play_0': 'Ham'}), follow=True)
        prod3 = Production.objects.order_by('-id')[0]
        self.assertRedirects(resp, '/play/%s/hamlet/production/%s/edit/cast' % (prod3.play.id32, prod3.id32))
        self.assertContains(resp, 'Editing production')
        self.assertContains(resp, 'Your addition has been stored; thank you.')
        self.assertContains(resp, 'Add new Part')

        # Add an existing person
        resp = self.client.post('/play/%s/hamlet/production/%s/edit/cast' % (prod3.play.id32, prod3.id32), {
            'person': 'Matthew',
            'production': prod3.id,
            'role': 'Director',
            'cast': '3',  # Crew
        })
        self.assertContains(resp, '/person/%s/matthew' % prod.parts.all()[0].id32)
        self.assertContains(resp, 'A new person also called &lsquo;Matthew&rsquo;')
        resp = self.client.post('/play/%s/hamlet/production/%s/edit/cast' % (prod3.play.id32, prod3.id32), {
            'person_choice': 'new',
            'person': 'Matthew',
            'production': prod3.id,
            'role': 'Director',
            'cast': '3',  # Crew
        }, follow=True)
        self.assertRedirects(resp, '/play/%s/hamlet/production/%s/edit/cast' % (prod3.play.id32, prod3.id32))
        self.assertContains(resp, 'Your new part has been added; thank you.')
        self.assertContains(resp, 'Matthew, Director <small>(Crew)</small>')

    def test_short_url(self):
        prod = make_production(
            'Hamlet',
            'A tragedy',
            ['Shakespeare Productions'],
            [{'name': 'Stirchley Theatre', 'start': '2013-01-01', 'end': '2013-01-14'}],
            [{'first': u'Matthew', 'last': u'Somerville', 'role': 'Laertes'}]
        )
        resp = self.client.get('/d/%s' % prod.id32)
        self.assertRedirects(resp, '/play/%s/hamlet/production/%s' % (prod.play.id32, prod.id32), status_code=301)


class CompanyTest(TestCase):
    def setUp(self):
        prod = make_production(
            'Hamlet',
            'A tragedy',
            ['Shakespeare Productions'],
            [{'name': 'Stirchley Theatre', 'start': '2013-01-01', 'end': '2013-01-14'}],
            [{'first': u'Matthew', 'last': u'Somerville', 'role': 'Laertes'}]
        )
        self.company_id = prod.companies.all()[0].id32

    def test_short_url(self):
        resp = self.client.get('/c/%s' % self.company_id)
        self.assertRedirects(resp, '/company/%s/shakespeare-productions' % self.company_id, status_code=301)

    def test_company_viewing(self):
        resp = self.client.get('/company/%s/shakes' % self.company_id, follow=True)
        self.assertRedirects(resp, '/company/%s/shakespeare-productions' % self.company_id, status_code=301)
        self.assertContains(resp, 'Stirchley Theatre')
        self.assertContains(resp, 'Hamlet')
        self.assertContains(resp, 'January 2013')

    def test_past(self):
        resp = self.client.get('/company/%s/shakespeare-productions/past' % self.company_id)
        self.assertContains(resp, 'Hamlet')

    def test_company_editing(self):
        resp = self.client.get('/company/%s/shakespeare-productions/add' % self.company_id)
        self.assertRedirects(resp, '/tickets?next=/company/%s/shakespeare-productions/add' % self.company_id)

        User.objects.create_user('test', password='test')
        self.client.login(username='test', password='test')

        resp = self.client.get('/company/%s/shakespeare-productions/add' % self.company_id)
        self.assertContains(resp, 'Adding production')
        self.assertContains(resp, 'Shakespeare Productions')

        resp = self.client.get('/company/%s/shakespeare-productions/edit' % self.company_id)
        self.assertContains(resp, 'Editing Shakespeare Productions')
        resp = self.client.post('/company/%s/shakespeare-productions/edit' % self.company_id, {
            'name': 'Ancient Shakespeare Productions',
            'description': 'Ancient company',
        }, follow=True)
        self.assertRedirects(resp, '/company/%s/ancient-shakespeare-productions' % self.company_id)
        self.assertContains(resp, 'Your changes have been stored; thank you.')
        self.assertContains(resp, 'Ancient company')
        self.assertContains(resp, 'Ancient Shakespeare Productions')
