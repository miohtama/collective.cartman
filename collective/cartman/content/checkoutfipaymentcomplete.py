"""Definition of the CheckoutFiPaymentComplete content type
"""

from zope.interface import implements, Interface

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from Products.ATContentTypes.configuration import zconf

# -*- Message Factory Imported Here -*-

from collective.cartman.config import PROJECTNAME

CheckoutFiPaymentCompleteSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

   atapi.TextField('successText',
        required=False,
        searchable=False,
        primary=False,
        validators = ('isTidyHtmlWithCleanup',),
        default_content_type = zconf.ATDocument.default_content_type,
        default_output_type = 'text/x-html-safe',
        allowable_content_types = zconf.ATDocument.allowed_content_types,
        widget = atapi.RichWidget(
            label = "Success Message",
            description = "Shown when payment success",
            rows = 8,
            allow_file_upload = zconf.ATDocument.allow_document_upload,
            ),
        ),

    atapi.TextField('failText',
        required=False,
        searchable=False,
        primary=False,
        validators = ('isTidyHtmlWithCleanup',),
        default_content_type = zconf.ATDocument.default_content_type,
        default_output_type = 'text/x-html-safe',
        allowable_content_types = zconf.ATDocument.allowed_content_types,
        widget = atapi.RichWidget(
            label = "Fail Message",
            description = "Shown when payment cancelled / did not success",
            rows = 8,
            allow_file_upload = zconf.ATDocument.allow_document_upload,
        ),
    ),

   atapi.TextField('alreadyOrderedText',
        required=False,
        searchable=False,
        primary=False,
        validators = ('isTidyHtmlWithCleanup',),
        default_content_type = zconf.ATDocument.default_content_type,
        default_output_type = 'text/x-html-safe',
        allowable_content_types = zconf.ATDocument.allowed_content_types,
        widget = atapi.RichWidget(
            label = "Already Ordered Message",
            description = "Text shown if the user tries to re-entry the same order twice (e.g. by hitting submit button twice or using Back navigation)",
            rows = 8,
            allow_file_upload = zconf.ATDocument.allow_document_upload,
            ),
        ),

    atapi.StringField('shopOwnerAddress',
        widget = atapi.StringWidget(
            label = "Shopw owner email",
            description = "Send notification from new orders to this email",
            rows = 8,
        ),
    ),


    atapi.StringField('customerEmailSubject',
        required=False,
        searchable=False,
        widget = atapi.StringWidget(
            label = "Customer email notification subject",
            description = "Send to the buyer.",
            rows = 8,
            ),
    ),

    atapi.TextField('customerEmail',
        required=False,
        searchable=False,
        primary=False,
        widget = atapi.TextAreaWidget(
            label = "Customer email notification message",
            description = "Send to the buyer. May contain template variables. Like $email, $firstName, $lastName",
            rows = 8,
            ),
        ),

    atapi.TextField('shopOwnerEmail',
        required=False,
        searchable=False,
        primary=False,
        widget = atapi.TextAreaWidget(
            label = "Customer email notification message",
            description = "Send to the buyer. May contain template variables.",
            rows = 8,
            ),
        ),

))

schemata.finalizeATCTSchema(CheckoutFiPaymentCompleteSchema, moveDiscussion=False)

CheckoutFiPaymentCompleteSchema["title"].default = "Order Received"

class ICheckoutFiPaymentComplete(Interface):
    """ """

class CheckoutFiPaymentComplete(base.ATCTContent):
    """Checkout.fi page returned from the payment processor"""
    meta_type = "CheckoutFiPaymentComplete"
    schema = CheckoutFiPaymentCompleteSchema

    implements(ICheckoutFiPaymentComplete)

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(CheckoutFiPaymentComplete, PROJECTNAME)
