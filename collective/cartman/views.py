"""


"""

import json

from zope.interface import Interface
from zope.component import getMultiAdapter
from five import grok

# Plone imports
from plone.app.layout.viewlets.interfaces import IHtmlHead
from plone.app.layout.viewlets.interfaces import IPortalHeader
from plone.app.layout.viewlets.interfaces import IPortalFooter

from utils import has_mini_cart

grok.templatedir("templates")
grok.context(Interface)

class ProductDataExtractor(grok.CodeView):
    """
    This view will extract JSON information from Plone content
    for Eric Cartman to be consumed.

    Override this view for your own products.
    """

    grok.name("product-data-extractor")

    def getData(self):
        """
        Extract product data from the current context item.

        Used for JSON payload.

        Override this method and class for your own products.

        Return None if this product does not support shopping.
        """
        data = {}

        data["id"] = self.context.UID()
        data["title"] = self.context.Title()
        data["title"] = self.context.Description()
        data["price"] = 5.0 # XXX: Use dummy price
        data["img"] = None

        return data

    def getJSON(self):
        data = self.getData()
        if data:
            return json.dumps(data)
        else:
            return None

    def render(self):
        return self.getJSON()

class AddToCartHelper(grok.View):
    """
    Subview to render add to cart on a page / viewlet.
    """

    grok.name("add-to-cart-helper")
    grok.template("add-to-cart")

    def update(self):
        extractor = getMultiAdapter((self.request, self.context), "product-data-extractor")
        self.data = extractor.getData()
        self.json = extractor.getJSON()
