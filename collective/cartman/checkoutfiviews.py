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

from collective.cartman.content.checkoutfipaypage import CheckoutFiPayPage
from collective.cartman.content.checkoutfipaymentcomplete import CheckoutFiPaymentComplete

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

    def getOrderAdapter(self):

        form = self.form = self.getForm()

        if not ORDER_ADAPTER_ID in form.objectIds():
            return None

        return form[ORDER_ADAPTER_ID]

    def getPaymentAdapter(self):

        form = self.form = self.getForm()

        if not "pay" in form.objectIds():
            return None

        return form["pay"]

    def updateOrderDataBySecret(self):
        """ Read order from the form storage, etc. """

        order_adapter = self.orderAdapter = self.getOrderAdapter()
        if not order_adapter:
            logger.warn("Could not find order adapter")
            return None

        self.order_secret = self.request.form.get("order-secret")
        if not self.order_secret:
            logger.warn("Order secret missing")
            return None

        self.orderRowId, self.data = order_adapter.getOrderBySecret(self.order_secret)
        if not self.data:
            logger.warn("Could not access order data")
            return None

        return True

    def updateOrderDataByReferenceNumber(self, referenceNumber):
        """ Read order from the form storage, etc. """

        order_adapter = self.orderAdapter = self.getOrderAdapter()
        if not order_adapter:
            logger.warn("Could not find order adapter")
            return None

        self.orderRowId, self.data = order_adapter.getOrderByReferenceNumber(referenceNumber)
        if not self.data:
            logger.warn("Could not access order data w/ reference number:", referenceNumber)
            return None

        return True


class CheckoutFiPayPage(grok.View, CheckoutFiFormGenView):

    # Don't show shopping cart on this view
    implements(IHideMiniCart)

    grok.context(CheckoutFiPayPage)
    grok.name("checkout-fi-pay")
    grok.template("checkout-fi-pay-page")

    def update(self):
        """
        """

        if not self.updateOrderDataBySecret():
            return None

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
        d["RETURN"] = self.form.absolute_url() + "/order-received"
        d["CANCEL"] = self.form.absolute_url()
        d["DELIVERY_DATE"] = datetime.date.today().strftime("%Y%m%d")
        d["REFERENCE"] = self.request.form["order-reference-number"]

        return checkoutfi.construct_checkout(orderId, self.context.getSecret(), d)


class CheckoutFiConfirmPage(grok.View, CheckoutFiFormGenView):
    """
    When returning from the payment processor.

    Handles all cases: OK, CANCEL, DELIVERED,DELAYED, etc.
    """
    # Don't show shopping cart on this view
    implements(IHideMiniCart)

    grok.context(CheckoutFiPaymentComplete)
    grok.name("checkout-fi-complete")
    grok.template("checkout-fi-complete-page")

    def getState(self):
        return self.state

    def updateOrderState(self):
        """
        Update the order record in Plone database with new status field.
        """

        # Update the order record to be completed
        if self.state == "OK":
            self.data["order-status"] = "payment-complete"
            self.orderAdapter.setRow(self.orderRowId, self.data)

    def update(self):

        # State is INVALID until further cleared
        self.state = "INVALID"

        request = self.request

        payment_adapter = self.getPaymentAdapter()
        if not payment_adapter:
            raise RuntimeError("Payment adapter missing")

        # Post request coming from PP
        if request.form.get("STATUS", None) is not None:

            if not checkoutfi.confirm_payment_signature(payment_adapter.getSecret(), request.form):
                logger.error("Bad MAC signature")
            else:
                status = request.form.get("STATUS", None)

                logger.warn("Form:", request.form)

                # Map to checkout.fi to our view internal state
                if status == "2":
                    self.state = "OK"

        else:
            logger.warn("Payment complete page did not get proper checkout.fi callback")

        if self.state != "INVALID":
            # Save paymet payment processor refernce
            ref = request.form.get("REFERENCE")
            self.updateOrderDataByReferenceNumber(ref)
            self.updateOrderState()

        logger.warn("Payment complete, final state:" + self.state)

    def templatize(self, template):
        """
        Replace template variables in the string.

        Use order data keys as template variables.
        """
        output = template
        for key, value in self.data:
            var = "$" + key
            output = output.replace(var, value)

        return output

    def sendEmail(self, receiver, template):
        """
        Send out an email notification.
        """

        if template is None:
            return

        if template.strip() == "":
            return

        email = receiver

        host = getToolByName(self, 'MailHost')
        # The `immediate` parameter causes an email to be sent immediately
        # (if any error is raised) rather than sent at the transaction
        # boundary or queued for later delivery.
        return host.send(mail_text, immediate=True)






