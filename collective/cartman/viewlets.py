"""


"""

from zope.interface import Interface
from five import grok

grok.templatedir("templates")

class MiniCart(grok.Viewlet):
    """ Cart summary line """

    # On every page, not checkout pages
    grok.content(zope.interface.Interface)

class MiniCart(grok.Viewlet):
    """ Cart summary line """

