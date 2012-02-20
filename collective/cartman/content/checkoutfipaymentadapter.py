"""Definition of the CheckoutFiPaymentAdapter content type
"""

from zope.interface import implements
from AccessControl import ClassSecurityInfo

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.CMFCore import permissions

from Products.PloneFormGen.content.actionAdapter import FormActionAdapter, \
    FormAdapterSchema

from collective.cartman.config import PROJECTNAME

CheckoutFiPaymentAdapterSchema = FormAdapterSchema.copy() + atapi.Schema((
    # -*- Your Archetypes field definitions here ... -*-
))

class CheckoutFiPaymentAdapter(FormActionAdapter):
    """ PFG to checkout.fi form submission.

    Handles cart payments via checkout.fi service.

    - Reads submission form, validates and calculates the total values

    - Constructs a signed <form> submission to the payment provider
      using keys configured in the adapter settings

    """

    meta_type = "CheckoutFiPaymentAdapter"
    schema = CheckoutFiPaymentAdapterSchema

    security = ClassSecurityInfo()

    security.declareProtected(permissions.View, 'onSuccess')
    def onSuccess(self, fields, REQUEST=None):
        """ The essential method of a PloneFormGen Adapter.

        - collect the submitted form data
        - create a dictionary of fields which have a counterpart in the
          table
        - add a row to the table where we set the value for these fields

        """
        print "Foo"

atapi.registerType(CheckoutFiPaymentAdapter, PROJECTNAME)
