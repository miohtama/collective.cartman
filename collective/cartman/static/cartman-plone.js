/**
 * Plone bindings for Eric Cartman
 */

/*global window,Cartman,CartmanUI,cartmanOptions*/

(function($) {

    "use strict";

    var cartman, ui;

    /**
     * If we detect PFG page and a certain field on it
     *
     * - Set this fields value to our JSON product payload
     *
     * - Print checout list on PFG form (non-editable)
     */
    function retrofitPloneFormGen() {
        var field = $(cartmanOptions.productFieldSelector);

        if(field.size() === 0) {
            return;
        }

        // Fill in <hidden> input with data to be posted to Plone server
        var productJSON = cartman.getContentsJSON();
        field.val(productJSON);

        // Render a <table> containing file product listing
        // using Transparency
        var data = ui.getCartTemplateData();

        // Template directives
        var directives = {

            // Show empty cart warning
            empty : function(elem) { if(data.count > 0) { elem.remove(); } },

            // Show empty cart warning
            filled : function(elem) { if(data.count <= 0) { elem.remove(); } },

            // Nested directives for product lines
            products : {
                price : function() { return ui.formatPrice(this.price); },
                total : function() { return ui.formatPrice(this.count*this.price); },
                // Fill in image column only if image URL is available
                "img@src" : function(elem) { if(this.img) { return this.img; } else { elem.remove(); } }
            }
        };

        var listing = $("<div>");

        var template = $(cartmanOptions.checkoutFormTemplateSelector);

        if(template.size() == 0) {
            throw new Error("Checkout form template missing:" + cartmanOptions.checkoutFormTemplateSelector);
        }

        // Explicitly used Transparency Template on jQuery node
        listing.data("template", template);

        // Render the template
        listing.render(data, directives);

        listing.insertAfter(field);
    }

    $(document).ready(function() {

        cartman = new Cartman();
        ui = new CartmanUI({
            cartman : cartman,
            selectors : {
                addToCartAnimator : "input[type=number]"
            }
        });

        // Bootstrap UI
        ui.init();

        // Integrate Plone checkout logic
        // We have defined checkout URL in viewlet
        // Javascript snippet.
        // When checkout is pressed we go to this URL
        ui.doCheckout = function() {
            // cartmanOptions is populated by a viewlet
            window.location = cartmanOptions.checkoutURL;
        };

        // Load cart from localStorage,
        cartman.refreshStore();

        retrofitPloneFormGen();
    });

})(jQuery);

