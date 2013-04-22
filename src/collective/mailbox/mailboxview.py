from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

class MailboxView(BrowserView):
    """
    Grade Book view browser view
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    def supports_mailbox(self):
        acl_users = getToolByName(self.context, 'acl_users')
        return hasattr(acl_users, 'my_emails')
        
    def get_mails(self):
        acl_users = getToolByName(self.context, 'acl_users')
        try:
            return acl_users.my_mails()
        except AttributeError:
            return {'outbox': [], 'inbox': []}
        