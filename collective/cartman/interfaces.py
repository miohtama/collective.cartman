from zope.interface import Interface

class IHideMiniCart(Interface):
    """
    Marker interface for views to tell that MiniCart should not append on these pages.
    """

