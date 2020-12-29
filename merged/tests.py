from django.test import TestCase
from django.core import mail

from theatricalia.tests import make_production


class MergeTest(TestCase):
    def test_doing_a_merge(self):
        make_production(
            'Hamlet',
            'A tragedy',
            ['Shakespeare Productions'],
            [{'name': 'Theatre', 'start': '2013-01-01', 'end': '2013-01-14'}]
        )
        make_production(
            'Hamlet',
            'A tragedy',
            ['Shakespeare Productions'],
            [{'name': 'Stirchley Theatre', 'start': '2013-01-01', 'end': '2013-01-14'}]
        )
        resp = self.client.get('/play/1/hamlet/production/1')
        self.assertContains(resp, 'Hamlet')
        resp = self.client.get('/play/1/hamlet/production/2')
        self.assertContains(resp, 'Hamlet')
        resp = self.client.get('/play/1/hamlet/production/2/merge')
        self.assertContains(resp, 'Thanks for helping improve the accuracy of the site.')
        resp = self.client.get('/play/1/hamlet/production/2')
        self.assertNotContains(resp, 'This is a duplicate')
        resp = self.client.get('/play/1/hamlet/production/1')
        self.assertContains(resp, 'This is a duplicate of Shakespeare Productions production of Hamlet')
        resp = self.client.post('/play/1/hamlet/production/1/merge', {'dupe': True})
        self.assertContains(resp, 'Thanks again for helping')
        self.assertEqual(len(mail.outbox), 1)

        resp = self.client.post('/play/1/hamlet/production/1/merge', {'stop': True}, follow=True)
        self.assertRedirects(resp, '/play/1/hamlet/production/1')
