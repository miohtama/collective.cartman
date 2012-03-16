# -*- coding: utf-8 -*-
"""

    Checkout.fi payment processor views

"""

import datetime
import json
import math
import logging
from odict import odict

from zope.interface import Interface, implements
from zope.component import getMultiAdapter, queryMultiAdapter
from five import grok
from Products.CMFCore.utils import getToolByName

from collective.cartman.interfaces import IHideMiniCart
from collective.cartman import checkoutfi

from collective.cartman.content.checkoutfipaypage import CheckoutFiPayPage
from collective.cartman.content.checkoutfipaymentcomplete import CheckoutFiPaymentComplete

grok.templatedir("templates")

ORDER_ADAPTER_ID="order"

PROCESSED_ITEM_ID="order-processed"

logger = logging.getLogger("checkout.fi")

class CheckoutFiFormGenView(object):
    """
    Helper methods used for content items in PFG payment form.

    These views can be applied for items which reside in PFG folder.
    """

    def getForm(self):
        return self.context.aq_parent

    def getOrderItem(self):
        """ Content item storing the orders """
        form = self.form = self.getForm()

        if not ORDER_ADAPTER_ID in form.objectIds():
            return None

        return form[ORDER_ADAPTER_ID]

    def getPaymentItem(self):
        """ Content item having merchandise id """
        form = self.form = self.getForm()

        if not "pay" in form.objectIds():
            return None

        return form["pay"]

    def getCompleteItem(self):
        """ Content item for thanks page """

        form = self.form = self.getForm()

        if not PROCESSED_ITEM_ID in form.objectIds():
            return None

        return form[PROCESSED_ITEM_ID]


    def updateOrderDataBySecret(self):
        """ Read order from the form storage, etc. """

        order_adapter = self.orderAdapter = self.getOrderItem()
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

        order_adapter = self.orderAdapter = self.getOrderItem()
        if not order_adapter:
            logger.warn("Could not find order adapter")
            return None

        self.orderRowId, self.data = order_adapter.getOrderByReferenceNumber(referenceNumber)
        if not self.data:
            logger.warn("Could not access order data w/ reference number:", referenceNumber)
            return None

        return True

    def getProducts(self):
        """
        @return: Iterable of products
        """
        if hasattr(self, "data"):
            s = self.data["product-data"]
            return json.loads(s)
        else:
            return []

    def calculateTotal(self, orderData):
        """
        All prices are tax included prices.

        @return: Total sum in floating point
        """
        order_sum = 0
        for product in orderData:
            order_sum += self.orderHelper.getTotalPrice(product)
        return order_sum


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

        #
        self.products = self.getProducts()

        self.orderHelper = getMultiAdapter((self.context, self.request), name="order-helper")

        total = self.total = self.calculateTotal(self.products)

        if not self.context.getSecret():
            raise RuntimeError("Merchant secret is not set")

        self.paymentData = self.createPaymentData(self.data["order-id"], total)

    def createPaymentData(self, orderId, total):
        """

        @param total: Price as float
        """

        # Checkout.fi data

        if total <= 0:
            raise RuntimeError("Could not calculate order total")

        d = {}

        # Convert to cents
        total = math.floor(total*100)
        d["AMOUNT"] = total

        d["MESSAGE"] = self.context.getMessage()
        d["MERCHANT"] = self.context.getSellerId()
        d["RETURN"] = self.form.absolute_url() + "/" + PROCESSED_ITEM_ID
        d["CANCEL"] = self.form.absolute_url() + "/" + PROCESSED_ITEM_ID
        d["DELIVERY_DATE"] = datetime.date.today().strftime("%Y%m%d")
        d["REFERENCE"] = self.request.form["order-reference-number"]

        return checkoutfi.construct_checkout(orderId, self.context.getSecret(), d)


class CheckoutFiConfirmPage(grok.View, CheckoutFiFormGenView):
    """
    When returning from the payment processor.

    Handles all cases: OK, CANCEL, DELIVERED,DELAYED, etc.

    Sample URL: http://localhost:9001/Plone/tietoja/tilaaminen/order-processed?VERSION=0001&STAMP=9&REFERENCE=97&PAYMENT=2834271&STATUS=2&ALGORITHM=2&MAC=874DB1883C5B3288AE25E0E287ED0282
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

        payment_adapter = self.getPaymentItem()
        if not payment_adapter:
            raise RuntimeError("Payment adapter missing")

        self.payment_adapter = payment_adapter

        self.orderHelper = getMultiAdapter((self.context, self.request), name="order-helper")

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

            self.sendCustomerEmail()
            self.sendShopOwnerEmail()

        logger.warn(u"Payment complete, final state:" + self.state)

    def getExtraTemplateVariables(self):
        """
        Get custom vars available in mini-templates.
        """
        return {}

    def templatize(self, template):
        """
        Replace template variables in the string.

        Use order data keys as template variables.
        """

        if type(template) != unicode:
            raise RuntimeError("Bad template:" + str(type(template)))


        output = template

        vars = odict()
        vars.update(self.data)
        vars.update(self.getExtraTemplateVariables())

        for key, value in vars.items():

            if type(value) == str:
                value = value.decode("utf-8")
            elif type(value) == unicode:
                value = value
            else:
                raise RuntimeError("Bad template data in " + key + " " + unicode(type(value)))

            var = u"$" + unicode(key)


            output = output.replace(var, value)

        return output

    def sendEmail(self, subject, receiver, template):
        """
        Send out an email notification.
        """

        if template is None:
            return

        if template.strip() == "":
            return

        # String replacement for template variables
        message = self.templatize(template)

        mailhost = getToolByName(self.context, 'MailHost')
        # The `immediate` parameter causes an email to be sent immediately
        # (if any error is raised) rather than sent at the transaction
        # boundary or queued for later delivery.

        # Site from address
        portal = self.context.portal_url.getPortalObject()
        source = portal.email_from_address
        # fromname = porta.xxx?

        try:
            print "Sending message:" + receiver
            print message
            mailhost.send(message,
                        receiver,
                        source,
                        subject=subject,
                        #subtype='plain',
                        charset="utf-8",
                        immediate = True)
        except Exception, e:
            # Gracefully handle SMTP errors
            import logging
            logger = logging.getLogger("ShopEmail")
            logger.exception(e)
            pass


    def sendCustomerEmail(self):
        """
        """
        data = self.data
        receiver = data["email"]
        complete = self.getCompleteItem()
        subject = complete.getCustomerEmailSubject().decode("utf-8")
        msg = complete.getCustomerEmail().decode("utf-8")
        self.sendEmail(subject, receiver, msg)

    def sendShopOwnerEmail(self):
        """
        """
        data = self.data
        complete = self.getCompleteItem()
        receiver = complete.getShopOwnerAddress()
        msg = complete.getShopOwnerEmail().decode("utf-8")
        subject = "Order #" + str(self.orderRowId)
        self.sendEmail("New order", receiver, msg)

    def getSuccessText(self):
        """

        """
        text = self.context.getSuccessText()
        text = text.decode("utf-8")
        return self.templatize(text)

