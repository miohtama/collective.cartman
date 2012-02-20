Introduction
============

Integrate `Eric Cartman <miohtama.github.com/Eric-Cartman>`_ with Plone.

This product may contain traces of nuts.


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


