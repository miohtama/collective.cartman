"""Definition of the CheckoutFiPaymentComplete content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from collective.cartman.config import PROJECTNAME

CheckoutFiPaymentCompleteSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

CheckoutFiPaymentCompleteSchema['title'].storage = atapi.AnnotationStorage()
CheckoutFiPaymentCompleteSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(CheckoutFiPaymentCompleteSchema, moveDiscussion=False)


class CheckoutFiPaymentComplete(base.ATCTContent):
    """Checkout.fi page returned from the payment processor"""
    meta_type = "CheckoutFiPaymentComplete"
    schema = CheckoutFiPaymentCompleteSchema

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(CheckoutFiPaymentComplete, PROJECTNAME)
