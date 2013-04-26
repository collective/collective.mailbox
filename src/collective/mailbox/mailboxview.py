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
        mailhost = getToolByName(self.context, 'MailHost')
        return hasattr(mailhost, 'my_mails')
        
    def get_mails(self):
        mailhost = getToolByName(self.context, 'MailHost')
        try:
            return mailhost.my_mails()
        except AttributeError:
            return {'outbox': [], 'inbox': []}
        
    def format_body(self, mailbody):
        mailbody = mailbody.replace('=\n', '')
        return mailbody.strip()