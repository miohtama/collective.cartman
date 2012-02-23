"""

    Checkout.fi payment processor views

"""

import datetime
import json
import math
import logging

from zope.interface import Interface, implements
from zope.component import getMultiAdapter, queryMultiAdapter
from five import grok

from collective.cartman.interfaces import IHideMiniCart
from collective.cartman import checkoutfi

from collective.cartman.content.checkoutfipaypage import CheckoutFiPayPage, ICheckoutFiPayPage

grok.templatedir("templates")

ORDER_ADAPTER_ID="order"

logger = logging.getLogger("checkout.fi")

class CheckoutFiFormGenView(object):
    """
    Helper methods used for content items in PFG payment form.

    These views can be applied for items which reside in PFG folder.
    """

    def getForm(self):
        return self.context.aq_parent

    def getPaymentAdapter(self):

        form = self.getForm()

        if not ORDER_ADAPTER_ID in form.objectIds():
            return None

        return form[ORDER_ADAPTER_ID]

class CheckoutFiPayPage(grok.View, CheckoutFiFormGenView):

    # Don't show shopping cart on this view
    implements(IHideMiniCart)

    grok.context(ICheckoutFiPayPage)
    grok.name("checkout-fi-pay")
    grok.template("checkout-fi-pay-page")

    def update(self):
        """
        """

        order_adapter = self.getPaymentAdapter()
        if not order_adapter:
            logger.warn("Could not find order adapter")
            return None

        self.order_secret = self.request.form.get("order-secret")
        if not self.order_secret:
            logger.warn("Order secret missing")
            return

        self.orderRowId, self.data = order_adapter.getOrderBySecret(self.order_secret)
        if not self.data:
            logger.warn("Could not access order data")
            return

        self.products = json.loads(self.data["product-data"])

        total = self.calculateTotal(self.products)

        if not self.context.getSecret():
            raise RuntimeError("Merchant secret is not set")

        self.paymentData = self.createPaymentData(self.data["order-id"], total)

    def calculateTotal(self, orderData):
        """
        All prices are tax included prices.

        @return: Total sum in cents
        """
        order_sum = 0
        for entry in orderData:
            order_sum += entry["price"]

        return math.floor(order_sum*100)

    def createPaymentData(self, orderId, total):
        """ """

        # Checkout.fi data
        d = {}

        d["AMOUNT"] = total
        d["MESSAGE"] = self.context.getMessage()
        d["MERCHANT"] = self.context.getSellerId()
        d["RETURN"] = self.context.absolute_url() + "/thank-you-for-order?order-secret=" + self.order_secret
        d["CANCEL"] = self.context.absolute_url() + "/payment-cancelled"
        d["DELIVERY_DATE"] = datetime.date.today().strftime("%Y%m%d")

        return checkoutfi.construct_checkout(orderId, self.context.getSecret(), d)

