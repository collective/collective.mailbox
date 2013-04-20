import unittest2 as unittest
from plone.api import user

from Products.CMFCore.utils import getToolByName

from collective.mailbox.testing import\
    COLLECTIVE_MAILBOX_INTEGRATION_TESTING

from collective.mailbox.mailhost import MailBoxHost

class TestExample(unittest.TestCase):

    layer = COLLECTIVE_MAILBOX_INTEGRATION_TESTING
    
    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.qi_tool = getToolByName(self.portal, 'portal_quickinstaller')
        user.create('fromer@foo.bar', 'fromer', 'secret')
        user.create('toer@foo.bar', 'toer', 'secret')
        user.create('toer2@foo.bar', 'toer2', 'secret')
    
    def test_product_is_installed(self):
        """ Validate that our products GS profile has been run and the product 
            installed
        """
        pid = 'collective.mailbox'
        installed = [p['id'] for p in self.qi_tool.listInstalledProducts()]
        self.assertTrue(pid in installed,
                        'package appears not to have been installed')
        # Make sure the mailbox got installed.
        self.assertTrue(isinstance(self.portal.MailHost, MailBoxHost))
        
    def test_mail(self):
        # Send a mail
        mh = self.portal.MailHost
        mh.simple_send('toer@foo.bar', 'fromer@foo.bar', 'Test subject', 'The body\nof the mail.\n')
        self.assertEqual(len(mh._emails), 1)

        # Multiple recipients
        mh.simple_send('toer@foo.bar,toer2@foo.bar', 'fromer@foo.bar', 'Test subject', 'The body\nof the mail.\n')
        self.assertEqual(len(mh._emails), 2)
        self.assertEqual(len(mh._outboxes['fromer']), 2)
        self.assertEqual(len(mh._inboxes['toer']), 2)
        self.assertEqual(len(mh._inboxes['toer2']), 1)
        
        # Non-user recipients doesn't increase inbox count.
        mh.simple_send('notauser@foo.bar', 'fromer@foo.bar', 'Test subject', 'The body\nof the mail.\n')
        self.assertEqual(len(mh._emails), 3)
        self.assertEqual(len(mh._inboxes), 2)
        
        # Sending from a non-user doesn't increase outbox count.
        mh.simple_send('toer@foo.bar', 'someoneelse@foo.bar', 'Test subject', 'The body\nof the mail.\n')
        self.assertEqual(len(mh._emails), 4)
        self.assertEqual(len(mh._outboxes), 1)

        # When noone is a users, it doesn't even get stored,
        mh.simple_send('notauser@foo.bar', 'someoneelse@foo.bar', 'Test subject', 'The body\nof the mail.\n')
        self.assertEqual(len(mh._emails), 4)
        