"""

    Cart viewlets.

"""
import json

from zope.interface import Interface
from zope.component import getMultiAdapter, queryMultiAdapter
from five import grok

# Plone imports
from plone.app.layout.viewlets.interfaces import IHtmlHead
from plone.app.layout.viewlets.interfaces import IPortalHeader
from plone.app.layout.viewlets.interfaces import IBelowContentTitle
from plone.app.layout.viewlets.interfaces import IPortalFooter
from plone.app.layout.viewlets.interfaces import IPortalTop

from utilities import has_mini_cart

grok.templatedir("templates")

# The generated HTML snippet going to <head>
TEMPLATE = u"""
<script type="text/javascript">
    var %(yourJavascriptSettingsGlobal)s = %(json)s;
</script>
"""

class JavascriptSettingsSnippet(grok.Viewlet):
    """ Include dynamic Javascript code in <head>.

    Include some code in <head> section which initializes
    Javascript variables. Later this code can be used
    by various scripts.

    Useful for settings.
    """

    grok.context(Interface)

    # This viewlet will be render()'ed in <head> section of Plone pages
    grok.viewletmanager(IHtmlHead)

    def getSettings(self):
        """
        @return: Python dictionary of settings
        """

        context = self.context.aq_inner
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')

        # Create youroptions Javascript object and populate in these variables
        return {
            # Pass dynamically allocated site URL to the Javascripts (virtual host monster thing)
            "staticMediaURL" : portal_state.portal_url() + "/++resource++collective.cartman",

            # Some other example parameters
            "portalURL" : portal_state.portal_url(),

            # Where to move for checkout
            "checkoutURL" : portal_state.portal_url() + "/checkout",

            # jQuery selector to retrofit PFG with product data
            "productFieldSelector" : "input[name=product-data]",

            # jQuery selector for the template which renders
            # PFG checkout form product <table>
            "checkoutFormTemplateSelector" : "#checkout-form-template"
        }


    def render(self):
        """
        Render the settings as inline Javascript object in HTML <head>
        """
        settings = self.getSettings()
        json_snippet = json.dumps(settings)

        # Use Python string template facility to produce the code
        html = TEMPLATE % { "yourJavascriptSettingsGlobal" : "cartmanOptions", "json" : json_snippet }

        return html

class MiniCart(grok.Viewlet):
    """ Cart summary line """

    # On every page, not checkout pages
    grok.context(Interface)
    grok.viewletmanager(IPortalHeader)

class CheckoutPopUp(grok.Viewlet):
    """ Pop-up window for checkout """
    grok.context(Interface)
    grok.viewletmanager(IPortalTop)
    grok.template("checkout-popup")

class ProductData(grok.Viewlet):
    """ Pop-up window for checkout """
    grok.context(Interface)
    grok.viewletmanager(IPortalFooter)
    grok.template("checkout-popup")


class CartTemplates(grok.Viewlet):
    """
    Client-side template sources for interactive cart elements
    """
    grok.context(Interface)
    grok.viewletmanager(IPortalFooter)
    grok.template("cart-templates")

class FormTemplates(grok.Viewlet):
    """
    Client-side template sources for checkout form.
    """
    grok.context(Interface)
    grok.viewletmanager(IPortalFooter)
    grok.template("form-templates")

class AddToCart(grok.Viewlet):
    """
    Default viewlet rendering add to basket <form>.

    Override or add functionality directly to your page template and hide.
    """
    grok.context(Interface)
    grok.viewletmanager(IBelowContentTitle)

    def render(self):
        view = queryMultiAdapter((self.context, self.request), name="add-to-cart-helper")

        if view:
            return view()
        else:
            # Don't break every page in the case of installation errors
            return ""