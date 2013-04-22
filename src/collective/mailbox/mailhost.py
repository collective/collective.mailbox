from rfc822 import Message
from DateTime import DateTime
from cStringIO import StringIO
from Products.MailHost.MailHost import MailHost
from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName

from BTrees.IOBTree import IOBTree
from BTrees.OOBTree import OOBTree
from BTrees.IIBTree import IITreeSet

from plone.api import user

try:
    from Products.PrintingMailHost.Patch import PrintingMailHost
except ImportError:
    PrintingMailHost = None

class MailBoxHost(MailHost):

    security = ClassSecurityInfo()
    
    def __init__(self,
                 id='',
                 title='',
                 smtp_host='localhost',
                 smtp_port=25,
                 force_tls=False,
                 smtp_uid='',
                 smtp_pwd='',
                 smtp_queue=False,
                 smtp_queue_directory='/tmp',
                ):
        """Initialize a new MailHost instance.
        """
        MailHost.__init__(self, id, title, smtp_host, smtp_port, force_tls,
                          smtp_uid, smtp_pwd, smtp_queue, smtp_queue_directory)
        self._emails = IOBTree()
        self._outboxes = OOBTree()
        self._inboxes = OOBTree()
        
    security.declarePrivate('_send')
    def _send(self, mfrom, mto, messageText, immediate=False):
        """ Send the message """

        # Send it immediately. We don't want to store mails that doesn't get
        # sent, mail shoud be delivered directly, always.
        MailHost._send(self, mfrom, mto, messageText, immediate=True)
        message = Message(StringIO(messageText))
        # I'm not sure you always get list here, so I handle both:
        if isinstance(mto, (str, unicode)):
            recipients = mto
            mto = mto.split(',')
        else:
            recipients = ','.join(mto)

        email = {'from': mfrom,
                 'to': recipients,
                 'date': DateTime(), # DateTime beacause timezones.
                 'subject': message.getheader('subject'),
                 'message': messageText[message.startofbody:]}

        try:
            key = self._emails.maxKey() + 1
        except ValueError:
            key = 0
        
        store = False
        current_user = user.get_current()
        if mfrom == current_user.getProperty('email'):
            # Only store if this is an email from the current user, and not a system email.
            sender_id = current_user.getId()
            if sender_id not in self._outboxes:
                self._outboxes[sender_id] = IITreeSet()
            self._outboxes[sender_id].add(key)
            store = True
        
        acl_users = getToolByName(self, 'acl_users')
        recipients = []
        for mail in mto:
            recipients.extend(acl_users.searchUsers(email=mail.strip()))
        for recipient in recipients:
            recipient_id = recipient['userid']
            if recipient_id not in self._inboxes:
                self._inboxes[recipient_id] = IITreeSet()
            self._inboxes[recipient_id].add(key)
            store = True
        
        if store:
            self._emails[key] = email
            
    security.declarePublic('my_mails')
    def my_mails(self):
        """Return a dictionary of emails"""

        user_id = user.get_current().getId()
        if user_id in self._inboxes:
            inbox = [self._emails[key] for key in self._inboxes[user_id]]
        else:
            inbox = []
        if user_id in self._outboxes:
            outbox = [self._emails[key] for key in self._outboxes[user_id]]
        else:
            outbox = []
        return {'inbox': inbox, 'outbox': outbox}
    
    