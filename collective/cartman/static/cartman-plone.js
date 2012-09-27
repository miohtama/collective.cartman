/**
 * Plone bindings for Eric Cartman
 */

/*global window,Cartman,CartmanUI,cartmanOptions,console*/

window.getCart = null;

(function($) {

    "use strict";

    var cartman, ui;

    /**
     * IE7 users need a pop-up because animation does not work
     */
    function onCartAdd() {
        //TODO: Add this
    }

    function sendEmail() {

        console.log("sendEmail()");

        var email = window.prompt("Anna vastaanottajan sähköpostiosoite:");

        function success(data) {
            // Got data from the server, proceed ->
            //
            $("#checkout-popup .checkout-footer .ajax").remove();
            //
            $("#checkout-popup .checkout-footer").append('<dl class="portalMessage info"><dt>Info</dt>' +
            '<dd>Viesti lähetetty osoitteeseen <b>' + email + '</b>.</dd>' +
            '</dl>');
        }

        function fail(jqXHR, textStatus, errorThrown) {
            var message = jqXHR.statusText || textStatus;
            $("#checkout-popup .checkout-footer .ajax").remove();
            console.error(message);
            window.alert("Matkasuunnitelman lähetys epäonnistui. Tarkistatko sähköpostiosoitteen ja yrität uudelleen.");
        }

        var data = {
            email : email,
            content : cartman.getContentsJSON()
        };

        // Retrieve list data from a JSON callback
        // which has been passed us in a global JS helper object
        function post() {
            $.ajax({
              url: window.cartmanOptions.portalURL + "/@@email-travel-plan",
              data: data,
              success: success,
              error : fail,
              type : "POST" // Bust Varnish cache
            });
        }

        // Enter async processing
        if(email) {
            $("#checkout-popup .checkout-footer").append('<img class="ajax" src="' + window.cartmanOptions.portalURL + "/spinner.gif" + '" />');
            post();
        }

    }

    // Patched dialog opener which will display help pop-up if the cart is empty
    function openCheckoutPopupWithHelp() {

        var cartman = window.getCart().cartman;

        // Show instructions if the cart is empty
        if(cartman.getContents().length === 0) {
            var foobar = $(".oma-kalajoki-button-hidden");
            foobar.click();
            return;
        }

        console.log("openCheckoutPopup()");
        var api = $("#checkout-popup").data("overlay");
        api.load();

        if($.browser.msie && $.browser.version == "8.0") {
            // Close button layout broken in IE8
            $("#checkout-popup .close").hide();
        }
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

        // Monkey-patch checkout dialog
        ui.openCheckoutPopup = openCheckoutPopupWithHelp;

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

        // Create email out button
        $("body").delegate(".emailButton", "click", sendEmail);
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

