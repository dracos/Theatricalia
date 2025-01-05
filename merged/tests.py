from django.test import TestCase
from django.core import mail

from theatricalia.tests import make_production


class MergeTest(TestCase):
    def test_doing_a_merge(self):
        hamlet1 = make_production(
            'Hamlet',
            'A tragedy',
            ['Shakespeare Productions'],
            [{'name': 'Theatre', 'start': '2013-01-01', 'end': '2013-01-14'}]
        )
        hamlet2 = make_production(
            'Hamlet',
            'A tragedy',
            ['Shakespeare Productions'],
            [{'name': 'Stirchley Theatre', 'start': '2013-01-01', 'end': '2013-01-14'}]
        )
        resp = self.client.get(hamlet1.get_absolute_url())
        self.assertContains(resp, 'Hamlet')
        resp = self.client.get(hamlet2.get_absolute_url())
        self.assertContains(resp, 'Hamlet')
        resp = self.client.post(hamlet2.get_absolute_url() + '/merge')
        self.assertContains(resp, 'Thanks for helping improve the accuracy of the site.')
        resp = self.client.get(hamlet2.get_absolute_url())
        self.assertNotContains(resp, 'This is a duplicate')
        resp = self.client.get(hamlet1.get_absolute_url())
        self.assertContains(resp, 'This is a duplicate of Shakespeare Productions production of Hamlet')
        resp = self.client.post(hamlet1.get_absolute_url() + '/merge', {'dupe': True})
        self.assertContains(resp, 'Thanks again for helping')
        self.assertEqual(len(mail.outbox), 1)

        resp = self.client.post(hamlet1.get_absolute_url() + '/merge', {'stop': True}, follow=True)
        self.assertRedirects(resp, hamlet1.get_absolute_url())
