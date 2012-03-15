"""


"""

import json

from zope.interface import Interface
from zope.component import getMultiAdapter, queryMultiAdapter
from five import grok

from utilities import has_mini_cart
from plone.uuid.interfaces import IUUID

from decimal import Decimal, ROUND_HALF_UP

TWOPLACES = Decimal("0.01")

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

        # Make sure we don't get UID from parent folder accidentally
        context = self.context.aq_base

        uid = sef.getUID()
        if not uid:
            return None

        # Stock keeping id
        # Visible to user
        data["id"] = uid

        # Product checkout list data management
        # points to Plone content
        data["uid"] = uid

        data["name"] = self.context.Title()
        data["url"] = self.context.absolute_url()
        data["description"] = self.context.Description()
        data["price"] = self.getPrice()
        data["img"] = None # URL for the image to be used in checkout list

        return data

    def getFormattedPrice(self):
        """
        Format float to two decimal places.
        """
        price = self.getPrice()
        if price is None:
            return None

        price = str(price)
        price = price.replace(",", ".")
        return Decimal(price).quantize(TWOPLACES, ROUND_HALF_UP)

    def getUID(self):
        """ AT and Dexterity compatible way to extract UID from a content item """
        # Make sure we don't get UID from parent folder accidentally
        context = self.context.aq_base
        # Returns UID of the context or None if not available
        uuid = IUUID(context, None)
        return uuid

    def getPrice(self):
        """
        This function is also used by the checkout processor.

        Override this to return real values for your shop.
        """

        return 5.0

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

