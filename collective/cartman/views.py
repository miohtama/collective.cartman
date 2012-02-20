"""


"""

import json

from zope.interface import Interface
from zope.component import getMultiAdapter, queryMultiAdapter
from five import grok

from utilities import has_mini_cart

grok.templatedir("templates")

class ProductDataExtractor(grok.CodeView):
    """
    This view will extract product data and JSON information from Plone content
    for the shopping cart to be consumed.

    Override this view for your own products.
    """

    grok.name("product-data-extractor")
    grok.context(Interface)

    def getData(self):
        """
        Extract product data from the current context item.

        Used for JSON payload.

        Override this method and class for your own products.

        Return None if this product does not support shopping.
        """
        data = {}

        if hasattr(self.context, "UID"):
            data["id"] = self.context.UID() # Stock keeping id
        else:
            # Not avail in portal root, Dexterity 1.0
            return None

        data["name"] = self.context.Title()
        data["url"] = self.context.absolute_url()
        data["description"] = self.context.Description()
        data["price"] = 5.0 # XXX: Use dummy price
        data["img"] = None # URL for the image to be used in checkout list

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
    grok.context(Interface)

    def update(self):

        context = self.context.aq_inner

        extractor = queryMultiAdapter((context, self.request), name="product-data-extractor")

        if extractor:
            self.data = extractor.getData()
            self.json = extractor.getJSON()
        else:
            self.data = self.json = None

