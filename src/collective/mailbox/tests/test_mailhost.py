import transaction
import unittest2 as unittest
from plone.api import user
from plone.app.testing import login, TEST_USER_NAME

from Products.CMFCore.utils import getToolByName

from collective.mailbox.testing import\
    COLLECTIVE_MAILBOX_INTEGRATION_TESTING, COLLECTIVE_MAILBOX_FUNCTIONAL_TESTING

from plone.testing.z2 import Browser

from collective.mailbox.mailhost import MailBoxHost

class TestMailHost(unittest.TestCase):

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
        
    def test_mailhost(self):
        # Send a mail
        login(self.portal, 'fromer')
        mh = getToolByName(self.portal, 'MailHost')
        mh.simple_send(['toer@foo.bar'], 'fromer@foo.bar', 'Test subject', 'The body\nof the mail.\n')
        self.assertEqual(len(mh._emails), 1)

        # Multiple recipients
        mh.simple_send(['toer@foo.bar','toer2@foo.bar'], 'fromer@foo.bar', 'Test subject', 'The body\nof the mail.\n')
        self.assertEqual(len(mh._emails), 2)
        self.assertEqual(len(mh._outboxes['fromer']), 2)
        self.assertEqual(len(mh._inboxes['toer']), 2)
        self.assertEqual(len(mh._inboxes['toer2']), 1)
        
        # Non-user recipients doesn't increase inbox count.
        mh.simple_send(['notauser@foo.bar'], 'fromer@foo.bar', 'Test subject', 'The body\nof the mail.\n')
        self.assertEqual(len(mh._emails), 3)
        self.assertEqual(len(mh._inboxes), 2)
        
        # Sending from a non-user doesn't increase outbox count.
        mh.simple_send(['toer@foo.bar'], 'someoneelse@foo.bar', 'Test subject', 'The body\nof the mail.\n')
        self.assertEqual(len(mh._emails), 4)
        self.assertEqual(len(mh._outboxes), 1)

        # When noone is a users, it doesn't even get stored,
        mh.simple_send(['notauser@foo.bar'], 'someoneelse@foo.bar', 'Test subject', 'The body\nof the mail.\n')
        self.assertEqual(len(mh._emails), 4)
        
        # You can retrieve your own emails, based on user_id:
        
        login(self.portal, TEST_USER_NAME)
        my_mails = mh.my_mails()
        self.assertEqual(my_mails, {'inbox': [], 'outbox': []})
        
        login(self.portal, 'fromer')
        my_mails = mh.my_mails()
        self.assertEqual(len(my_mails['inbox']), 0)
        self.assertEqual(len(my_mails['outbox']), 3)

        login(self.portal, 'toer')
        my_mails = mh.my_mails()
        self.assertEqual(len(my_mails['inbox']), 3)
        self.assertEqual(len(my_mails['outbox']), 0)


class TestViews(unittest.TestCase):

    layer = COLLECTIVE_MAILBOX_FUNCTIONAL_TESTING
    
    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.qi_tool = getToolByName(self.portal, 'portal_quickinstaller')
        user.create('fromer@foo.bar', 'fromer', 'secret')
        user.create('toer@foo.bar', 'toer', 'secret')
        user.create('toer2@foo.bar', 'toer2', 'secret')
    
        login(self.portal, 'fromer')
        mh = getToolByName(self.portal, 'MailHost')
        mh.simple_send('toer@foo.bar', 'fromer@foo.bar', 'Test subject 1', 'This is a mail body.\n')
        mh.simple_send('toer@foo.bar,toer2@foo.bar', 'fromer@foo.bar', 'Test subject 2', 'The body\nof the mail.\n')
        transaction.commit()
        
    def test_outbox(self):
        browser = Browser(self.app)
        browser.handleErrors = False
        browser.addHeader('Authorization', 'Basic %s:%s' % ('fromer', 'secret',))

        portalURL = self.portal.absolute_url()
        browser.open(portalURL)
        self.assertIn('fromer', browser.contents)
        
        browser.open(portalURL+'/@@my_mailbox')

        self.assertIn('toer@foo.bar', browser.contents)
        self.assertIn('toer2@foo.bar', browser.contents)
        self.assertIn('Test subject 1', browser.contents)
        self.assertIn('This is a mail body.', browser.contents)
        self.assertIn('Test subject 2', browser.contents)        
        self.assertIn('The body\nof the mail.', browser.contents)
        
        self.assertNotIn('fromer@foo.bar', browser.contents)

        browser = Browser(self.app)
        browser.handleErrors = False
        browser.addHeader('Authorization', 'Basic %s:%s' % ('toer', 'secret',))
        browser.open(portalURL+'/@@my_mailbox')
        self.assertIn('fromer@foo.bar', browser.contents)
        