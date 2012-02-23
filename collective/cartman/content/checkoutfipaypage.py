# -*- coding: utf-8 -*-
"""Definition of the CheckoutFiPayPage content type
"""
import math
import datetime

from zope.interface import implements, Interface

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.CMFCore import permissions

# -*- Message Factory Imported Here -*-

from collective.cartman.config import PROJECTNAME
from collective.cartman import checkoutfi

from Products.PloneFormGen.interfaces import IPloneFormGenThanksPage



CheckoutFiPayPageSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-
    atapi.StringField("sellerId",
        read_permission=permissions.ModifyPortalContent,
        write_permission=permissions.ModifyPortalContent,
        widget=atapi.StringWidget(label=u"Myyjän tunniste")
    ),

    atapi.StringField("secret",
                read_permission=permissions.ModifyPortalContent,
                write_permission=permissions.ModifyPortalContent,
                widget=atapi.StringWidget(label=u"Turva-avain")
    ),

    atapi.StringField("message",
                read_permission=permissions.ModifyPortalContent,
                write_permission=permissions.ModifyPortalContent,
                widget=atapi.StringWidget(label=u"Viesti maksajan tiliotteelle")
    ),

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

CheckoutFiPayPageSchema['title'].storage = atapi.AnnotationStorage()
CheckoutFiPayPageSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(CheckoutFiPayPageSchema, moveDiscussion=False)

class ICheckoutFiPayPage(Interface):
    """ """

class CheckoutFiPayPage(base.ATCTContent):
    """Checkout.fi payment page"""

    implements(IPloneFormGenThanksPage, ICheckoutFiPayPage)

    meta_type = "CheckoutFiPayPage"
    schema = CheckoutFiPayPageSchema

    # -*- Your ATSchema to Python Property Bridges Here ... -*-



atapi.registerType(CheckoutFiPayPage, PROJECTNAME)
