from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import applyProfile
from plone.testing import z2

from zope.configuration import xmlconfig

import Products.PrintingMailHost

class CollectiveMailbox(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Required by Products.CMFPlone:plone-content
        #z2.installProduct(app, 'Products.PythonScripts')
        # Load ZCML for this package
        import collective.mailbox
        xmlconfig.file('configure.zcml',
                       collective.mailbox,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        # Installs all the Plone stuff. Workflows etc.
        #applyProfile(portal, 'Products.CMFPlone:plone')
        # Install portal content. Including the Members folder!
        #applyProfile(portal, 'Products.CMFPlone:plone-content')
        
        applyProfile(portal, 'collective.mailbox:default')

COLLECTIVE_MAILBOX_FIXTURE = CollectiveMailbox()
COLLECTIVE_MAILBOX_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(COLLECTIVE_MAILBOX_FIXTURE, ),
                       name="CollectiveMailbox:Integration")

COLLECTIVE_MAILBOX_FUNCTIONAL_TESTING = \
    FunctionalTesting(bases=(COLLECTIVE_MAILBOX_FIXTURE, ),
                       name="CollectiveMailbox:Functional")
