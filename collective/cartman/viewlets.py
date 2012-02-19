"""


"""

from zope.interface import Interface
from zope.component import getMultiAdapter, queryMultiAdapter
from five import grok

# Plone imports
from plone.app.layout.viewlets.interfaces import IHtmlHead
from plone.app.layout.viewlets.interfaces import IPortalHeader
from plone.app.layout.viewlets.interfaces import IBelowContentTitle
from plone.app.layout.viewlets.interfaces import IPortalFooter
from plone.app.layout.viewlets.interfaces import IPortalTop

from utils import has_mini_cart

grok.templatedir("templates")

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