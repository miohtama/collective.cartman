# -*- coding: utf-8 -*-
"""Definition of the CheckoutFiPaymentAdapter content type
"""
import json
import math
import datetime
import random
from odict import odict
from types import StringTypes

from zope.interface import implements
from zope.component import getMultiAdapter
from AccessControl import ClassSecurityInfo
from DateTime import DateTime

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName

from Products.PloneFormGen.content.actionAdapter import FormActionAdapter, FormAdapterSchema

from Products.PloneFormGen.content.saveDataAdapter import FormSaveDataAdapter

from plone.app.uuid.utils import uuidToObject

from collective.cartman.config import PROJECTNAME
from collective.cartman import checkoutfi
# JSON product data field id
PRODUCT_DATA_FIELD="product-data"

# Example: http://svn.plone.org/svn/collective/Products.PloneFormGen/adapters/Products.sqlpfgadapter/trunk/Products/sqlpfgadapter/content/sqlAdapter.py
CheckoutFiPaymentAdapterSchema = FormSaveDataAdapter.schema.copy() + atapi.Schema((
    # -*- Your Archetypes field definitions here ... -*-


    atapi.IntegerField("orderId",
                required=True,
                default=1,
                read_permission=permissions.ModifyPortalContent,
                write_permission=permissions.ModifyPortalContent,
                widget=atapi.IntegerWidget(label=u"Next order id", description=u"Increments +1 for each new payment attempt")
    ),


))

CheckoutFiPaymentAdapterSchema["title"].default = "Checkout.fi payment"

class CheckoutFiPaymentAdapter(FormSaveDataAdapter):
    """ PFG to checkout.fi form submission.

    Handles cart payments via checkout.fi service.

    - Reads submission form, validates and calculates the total values

    - Constructs a signed <form> submission to the payment provider
      using keys configured in the adapter settings

    T

    """

    meta_type = "CheckoutFiPaymentAdapter"
    schema = CheckoutFiPaymentAdapterSchema

    security = ClassSecurityInfo()

    def filterProductData(self, orderData):
        """
        Extract counts and product ids from the order and count their real prices.
        This for the case that the user does not submit bad order data.

        """

        data = []

        reference_catalog = getToolByName(self, "reference_catalog")

        # Silently ignore bad counts
        good_entries =[ entry for entry in orderData if entry["count"] > 0]

        for entry in good_entries:
            uid = entry["UID"]
            if not uid:
                raise RuntimeError(u"Product data entry missing UID:", entry)


            obj = uuidToObject(uid)
            if not obj:
                # Could not find object
                raise RuntimeError(u"Could not look-up UUID:", uid)


            product_data_extractor = getMultiAdapter((obj, self.REQUEST), name="product-data-extractor")

            # Set price etc. on the server-side
            # only count can come from the client

            real_data = product_data_extractor.getData()
            if real_data is None:
                raise RuntimeError("Could not get product data for UID:" + uid)

            real_data["count"] = entry["count"]
            data.append(real_data)

        return data


    def getFieldById(self, fields, fid):
        """

        """
        for f in fields:
            if f.getId() == fid:
                return f
        return None

    def extractProductData(self, fields):
        """
        Extract products JSON payload from the product data field as filled in by JS.
        """

        dataf = self.getFieldById(fields, PRODUCT_DATA_FIELD)
        if dataf is None:
            raise RuntimeError("Your form lacks productdata field")


        value = self.REQUEST.form.get(dataf.__name__, None)
        if not value:
            raise RuntimeError("No order data")

        try:
            data = json.loads(value)
        except:
            raise RuntimeError("Order data is corrupted")

        return data

    def getOrderBySecret(self, orderSecret):
        """
        @return (id, order data) or (None, None)
        """
        names = self.getColumnNames()
        order_secret_index = names.index("order-secret")

        if orderSecret in ["", None]:
            raise RuntimeError("Missing order-secret value")

        if not order_secret_index:
            raise RuntimeError("Badly configured PFG payment form, lacks order-secret field")

        def dictify(row):
            data = odict()
            i = 0
            for name in names:
                data[name] = row[i]
                i += 1
            return data

        for order_row_id, row in self._inputStorage.items():
            if row[order_secret_index] == orderSecret:
                return order_row_id, dictify(row)

        return None, None


    def getReturnURL(self):
        """
        """
        return self.absolute_url() + "/thank-you"

    def getCancelURL(self):
        return self.absolute_url() + "/no-go"

    def nextOrderId(self):
        """
        """
        orderId = self.getOrderId()
        orderId = int(orderId)
        self.setOrderId(orderId+1)
        return self.orderId

    def setRow(self, id, value):
        """
        Update row contents.
        """

        assert isintance(value, odict)
        seq = [ val for val in value.values() ]
        self._inputStorage[id] = seq

    def saveRow(self, fields, REQUEST):

        # https://github.com/smcmahon/Products.PloneFormGen/blob/master/Products/PloneFormGen/content/saveDataAdapter.py

        data = []
        for f in fields:
            if not f.isLabel():
                val = REQUEST.form.get(f.fgField.getName(),'')
                if not type(val) in StringTypes:
                    # Zope has marshalled the field into
                    # something other than a string
                    val = str(val)
                data.append(val)

        if self.ExtraData:
            for f in self.ExtraData:
                if f == 'dt':
                    data.append( str(DateTime()) )
                else:
                    data.append( getattr(REQUEST, f, '') )


        self._addDataRow( data )

    security.declareProtected(permissions.View, 'onSuccess')
    def onSuccess(self, fields, REQUEST=None):
        """ The essential method of a PloneFormGen Adapter.

        - collect the submitted form data
        - create a dictionary of fields which have a counterpart in the
          table
        - add a row to the table where we set the value for these fields

        """

        # https://github.com/smcmahon/Products.PloneFormGen/blob/master/Products/PloneFormGen/content/actionAdapter.py


        try:
            productData = self.extractProductData(fields)
        except Exception, e:
            return dict(PRODUCT_DATA_FIELD=unicode(e))

        if len(productData) == 0:
            return dict(PRODUCT_DATA_FIELD=u"Please select products to your shopping cart first")

        # Fix server side prices, counts
        # against potential malicious attacks.
        # Repopulate order data with good known
        # values from the server-side and
        # make sure client can only post UIDs and counts for items.

        # XXX: In this context this really doesn't do anything but
        # validates the data
        productData = self.filterProductData(productData)

        # Fill in these so that
        orderSecret = str(random.randint(0, 999999999))
        REQUEST.form["order-id"] = self.nextOrderId()
        REQUEST.form["order-secret"] = orderSecret
        REQUEST.form["order-status"] = "waiting-payment"

        # Validated product data
        REQUEST.form[PRODUCT_DATA_FIELD] = json.dumps(productData)

        self.saveRow(fields, REQUEST)


atapi.registerType(CheckoutFiPaymentAdapter, PROJECTNAME)
