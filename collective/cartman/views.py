"""


"""

import json
import logging
from StringIO import StringIO

from zope.interface import Interface
from zope.component import getMultiAdapter, queryMultiAdapter
from five import grok

from utilities import has_mini_cart
from plone.uuid.interfaces import IUUID
from plone.app.uuid.utils import uuidToObject
from Products.CMFCore.utils import getToolByName

from Products.CMFCore.interfaces import ISiteRoot

from decimal import Decimal, ROUND_HALF_UP

TWOPLACES = Decimal("0.01")

grok.templatedir("templates")

logger = logging.getLogger("cart")

def safe_float(val):
    """ """

    if type(val) == str or type(val) == unicode:
        val = val.replace(",", ".")

    val = float(val)

    return val

class HelperBaseView(grok.CodeView):
    """ """

    grok.baseclass()

    def formatPrice(self, price):
        """
        """
        price = str(price)
        price = price.replace(",", ".")
        return unicode(Decimal(price).quantize(TWOPLACES, ROUND_HALF_UP))

    def formatWeight(self, weight):
        """
        """
        weight = str(weight)
        weight = weight.replace(",", ".")
        return unicode(Decimal(weight).quantize(TWOPLACES, ROUND_HALF_UP))

    def getTotalPrice(self, product):
        """
        """
        try:
            return safe_float(product.get("price", 0)) * safe_float(product.get("count", 0))
        except Exception, e:
            logger.error("Could not calcualte price")
            logger.exception(e)

            try:
                logger.error(u"%s" % product.get("price", None))
                logger.error(u"%s" % product.get("count", None))
            except:
                pass
            return 99999999

    def getTotalWeight(self, product):
        """
        """
        try:
            weight = safe_float(product.get("weight", 0))
            return weight * safe_float(product.get("count", 0))
        except Exception, e:
            logger.exception(e)
            return 0

class ProductDataExtractor(HelperBaseView):
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

        uid = self.getUID()
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

        if hasattr(context, "image"):
            img = self.context.absolute_url() + "/@@images/image"
        elif "leadImage" in context.Schema():
            # collective.contentleadimage
            images = self.context.unrestrictedTraverse("@@images")
            scale = images.scale('leadImage', width=280, height=280)
            if scale:
                img = scale.absolute_url()
            else:
                img = None
        else:
            img = None

        data["img"] = img

        return data

    def getFormattedPrice(self):
        """
        Format float to two decimal places.
        """
        price = self.getPrice()
        if price is None:
            return None

        return self.formatPrice(price)

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
            self.extractor = extractor
            self.data = extractor.getData()
            self.json = extractor.getJSON()
        else:
            self.data = self.json = self.extractor = None


class OrderHelper(HelperBaseView):
    """
    Manipulate order data based on the choices the user makes on the order from.

    E.g. like delivery option.

    You need to override this view for custom site logic.
    """

    grok.name("order-helper")
    grok.context(Interface)

    def process(self, productData, request):
        """
        @param productData: Cleaned product data extracted from the order form as list of dicts

        @param request: HTTP request containing PloneFormGen HTTP request submission payload

        @return: Updated product data odict
        """
        return productData

    def render(self):
        return "Call helper methods instead"


class GenerateText(grok.CodeView):
    """
    Generate plain text presentation of the cart
    """
    grok.name("cart-generate-text")
    grok.context(ISiteRoot)

    def filterProductData(self, orderData):
        """
        Extract counts and product ids from the order and count their real prices.
        This for the case that the user does not submit bad order data.
        """

        data = []

        # Silently ignore bad counts
        good_entries = [entry for entry in orderData if entry["count"] > 0]

        for entry in good_entries:
            uid = entry["uid"]
            if not uid:
                raise RuntimeError(u"Product data entry missing UID:", entry)

            obj = uuidToObject(uid)
            if not obj:
                # Could not find object
                raise RuntimeError(u"Could not look-up UUID:", uid)

            product_data_extractor = getMultiAdapter((obj, self.request), name="product-data-extractor")

            # Set price etc. on the server-side
            # only count can come from the client

            real_data = product_data_extractor.getData()
            if real_data is None:
                raise RuntimeError("Could not get product data for UID:" + uid)

            real_data["count"] = entry["count"]
            data.append(real_data)

        return data

    def render(self):
        """
        """
        data = self.data

        data = self.filterProductData(data)

        buf = StringIO()
        for product in data:
            print >> buf, product["name"]
            print >> buf, product["url"]
            print >> buf, "-" * 76
            print >> buf, product["description"]
            print >> buf, ""
            print >> buf, ""

        return buf.getvalue()


class EmailPlan(grok.CodeView):
    """
    Email travel planner
    """
    grok.name("email-travel-plan")
    grok.context(ISiteRoot)

    def render(self):

        if self.request["REQUEST_METHOD"] != "POST":
            raise RuntimeError("Bad method")

        receiver = self.request.form.get("email", None)
        data = self.request.form["content"]

        generator = GenerateText(self.context, self.request)
        generator.data = json.loads(data)
        message = generator()

        mailhost = getToolByName(self.context, 'MailHost')
        # The `immediate` parameter causes an email to be sent immediately
        # (if any error is raised) rather than sent at the transaction
        # boundary or queued for later delivery.

        # Site from address
        portal = self.context.portal_url.getPortalObject()
        source = portal.email_from_address
        # fromname = porta.xxx?

        subject = "Oma Kalajoki Matkasuunnitelmasi"

        try:

            try:
                logger.info(u"Sending message:" + receiver)
                logger.info(message)
            except Exception as e:
                logger.exception(e)

            mailhost.send(message,
                        receiver,
                        source,
                        subject=subject,
                        #subtype='plain',
                        charset="utf-8",
                        immediate=True)
        except Exception as e:
            logger.exception(e)
            raise

        logger.info("Emailing done")

