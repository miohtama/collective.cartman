from zope.interface import Interface

class HideMiniCart(Interface):
    """
    Marker interface for views to tell that MiniCart should not append on these pages.
    """

