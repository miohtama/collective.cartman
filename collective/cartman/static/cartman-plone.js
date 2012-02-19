/**
 * Plone bindings for Eric Cartman
 */

/*global Cartman,CartmanUI*/

(function($) {

    "use strict";

    $(document).ready(function() {

        var cartman = new Cartman();
        var ui = new CartmanUI({
            cartman : cartman,
            selectors : {
                addToCartAnimator : "button"
            }
        });

        // Bootstrap UI
        ui.init();

        // Load cart from localStorage,
        cartman.refreshStore();

    });

})(jQuery);

