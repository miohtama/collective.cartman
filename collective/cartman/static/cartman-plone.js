/**
 * Plone bindings for Eric Cartman
 */

/*global window,Cartman,CartmanUI,cartmanOptions*/

window.getCart = null;

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

        console.log("Retrofit PFG");

        // Fill in <hidden> input with data to be posted to Plone server
        var productJSON = cartman.getContentsJSON();
        field.val(productJSON);

        // Render a <table> containing file product listing
        // using Transparency
        var data = ui.getCartTemplateData();

        console.log("Data:");
        console.log(data);

        // Template directives
        var directives = {

            // Show empty cart warning
            'checkout-data-container' : function(elem) {
                var $elem = $(elem);

                if(cartman.hasContent()) {
                    $elem.addClass("has-items");
                } else {
                    $elem.removeClass("has-items");
                }
             },

            // Nested directives for product lines
            products : {
                price : function() { return ui.formatPrice(this.price); },
                total : function() { return ui.formatPrice(this.count*this.price); },
                // Fill in image column only if image URL is available
                // Set image source or hide image
                'product-img' : function(elem) {
                    elem = $(elem);
                    if(this.img) {
                        elem.attr("src", this.img);
                    } else {
                        elem.hide();
                    }
                }
            }
        };

        var listing = $("<div>");

        var template = $(cartmanOptions.checkoutFormTemplateSelector);

        if(template.size() === 0) {
            throw new Error("Checkout form template missing:" + cartmanOptions.checkoutFormTemplateSelector);
        }

        listing.append(template.children().clone());

        // Render the template
        listing.render(data, directives, true);

        listing.insertAfter(field);
    }

    /**
     * IE7 users need a pop-up because animation does not work
     */
    function onCartAdd() {
        //TODO: Add this
    }

    function initCartman() {

        // No double init
        if(cartman) {
            return {
                cartman : cartman,
                ui : ui
            };
        }

        cartman = new Cartman();

        ui = new CartmanUI({
            cartman : cartman,
            selectors : {
                addToCartAnimator : ".add-count"
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

        // IE specific add to cart message
        cartman.on("cartadd", onCartAdd);

        if(window.setupCartman) {
            window.setupCartman(cartman, ui);
        }

        // Load cart from localStorage,
        cartman.refreshStore();

        retrofitPloneFormGen();

    }

    // Explose as global
    window.getCart = function() {

        initCartman();

        // No double init
        return {
            cartman : cartman,
            ui : ui
        };

    };

    $(document).ready(function() {
        initCartman();
    });

})(jQuery);

