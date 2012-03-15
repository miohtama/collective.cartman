Introduction
============

Integrate `Eric Cartman <miohtama.github.com/Eric-Cartman>`_ with Plone.

This product may contain traces of nuts.

Requirements
=============

Dexterity 1.1+, must have UIDs enabled to all shoppable content

PloneFormGen 1.7

Usage
=========

Create checkout form
----------------------

Create PloneFormGen form.

Add whatever fields you wish to use to ask checkout data

Product data field on checkout form
---------------------------------------

Add a new string field to PloneFormGen form with id ``product-data``

* Field is hidden

* Max length of 9999

Order id field on checkout form
----------------------------------
Add a new string field to PloneFormGen form with id ``order-id``

* Field is hidden

* Field is not requird

Order reference number field on checkout form
-------------------------------------------------

Add a new string field to PloneFormGen form with id ``order-reference-number``
Field is used for bank payments tracking.

* Field is hidden

* Field is not required

Order secret field on checkout form
------------------------------------

Add a new string field to PloneFormGen form with id ``order-secret``

* Field is hidden

* Field is not requird

This is a non-guessable id of the order.

Order status field on checkout form
------------------------------------

Add a new string field to PloneFormGen form with id ``order-status``

* Field is hidden

* Field is not requird

This contains text string "waiting-payment" or "payment-complete",
depending whether the user succefully returned from the payment
site.

Order adapter
-----------------

Install order adapter as the only active Action Adapter of the form.
This is used to store order in the PloneFormGen database.

It will advance automatically to the chosen Pay page.

The adapter type: CheckoutFiPaymentAdapter

The adapter id must be ``order``.

Pay page
--------------------------

This is a PloneFormGen thanks page of type ``CheckoutFiPayPage``.
It will create a ``<form>`` which will be submitted to the
payment processor automatically via Javascript.

The pay page must be selected as "Thank you page" on PloneFormGet Edit tab.

Currently checkout.fi payments supported

* Add your merchant id

* Add your shared secret

* Add other data

Payment complete
--------------------------

This is a PloneFormGen thanks page of type ``CheckoutFiPaymentCompletePage``.
Payment processor will submit HTTT POST to this page
when the payment is completed. The page logic will extract
variables from POST and update the order status in the save adapter.

The id of this page must be ``order-processed``.

Payment cancelled
--------------------------

This is a PloneFormGen thanks page of type ``CheckoutFiPayPage``.

The id of this page must be ``payment-cancelled``.

The payment processor will redirect here if the user cancels the payment.

How tos
=========

Adding a new payment adapter
-------------------------------

How to add your payment provider support to PloneFormGen.

* Generate AT content type using ZopeSkel templates, global_allow=false

* Change base class and base schema to PloneFormGen adapter

* Edit FormFolder.xml to allow adding into FormFolder

* Add in onSuccess() method which de-serializes form submission,
  validates and calculates final totals

Misc
=====

Contains Twitter Bootstrap 2.0 icon kit adaption for Plone.