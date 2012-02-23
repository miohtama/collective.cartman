# -*- coding: utf-8 -*-
"""

    Checkout.fi payment service implementation in Python

    http://checkout.fi/ohjelmistopaketit.html

    Use Nordea bank in the need of test bank.

"""

import logging
from time import time
from odict import odict
import hashlib

logger = logging.getLogger("checkout.fi")

def create_reference_number(orderId):
    """
    Calculate Finnish "viitenumero"

    http://groups.google.com/group/sfnet.atk.ohjelmointi/msg/a37525d03dfabc19
    """

    digits = str(orderId)
    i = 0
    weights = [7,3,1]
    total = 0
    for d in digits:
        d = int(d)
        total += d * weights[i % 3]
        i += 1

    check_digit = (10 - (total % 10)) % 10

    return digits + str(check_digit)

def calculate_mac(secret, data, separator="+", secret_at_end=True):
    """
    @param data: odict
    """
    # calculate MAC
    concat = separator.join(data.values())

    #logger.warn(o)

    # Hashed string should look like
    # 0001+1329982892+1000+12344+Huonekalutilaus Paljon puita, lehtiÃ¤ ja muttereita+FI+375917+http://demo1.checkout.fi/xml2.php?test=1++++FIN+EUR+1+1+0+2+20120223+Tero+Testaaja+Ã„Ã¤kkÃ¶stie 5b3 Kulmaravintolan ylÃ¤kerta+33100+Tampere+SAIPPUAKAUPPIAS0001+1329982893+1000+12344+Huonekalutilaus Paljon puita, lehtiÃ¤ ja muttereita+FI+375917+http://demo1.checkout.fi/xml2.php?test=1
    # ++++FIN+EUR+10+1+0+2+20120223+Tero+Testaaja+Ã„Ã¤kkÃ¶stie 5b3 Kulmaravintolan ylÃ¤kerta+33100+Tampere+SAIPPUAKAUPPIAS

    # 0001+3+1500+39+verkkokauppa+FI+375917+http://localhost:9001/Plone/tietoja/tilaaminen/pay/thank-you-for-order?order-secret=944379638+http://localhost:9001/Plone/tietoja/tilaaminen/pay/payment-cancelled
    # +++FIN+EUR+1+1+0+1+20120223+++++
    #logger.warn(concat)

    if not secret:
        raise RuntimeError("Missing shared secret")

    # WHYYY they can't do things in one way?
    if secret_at_end:
        concat += separator + secret
    else:
        concat = secret + separator + concat

    logger.warn("Mac data:" + concat)

    m = hashlib.md5()
    m.update(concat)

    return m.hexdigest().upper()


def construct_checkout(orderId, secret, data):
    """
    Create checkout.fi FORM PORT parameters.

    @param data: Dictionary of to be filled in fields as in API document
    """

    def get_required(name):
        val = data.get(name, None)
        if not val:
            raise RuntimeError("Missing Checkout.Fi parameter:" + name)
        return val

    #    public function generateCheckout($data) {
    #        foreach($data as $key => $value) {
    #            $this->{$key}=$value;
    #        }
    #        $mac=strtoupper(md5("{$this->version}+{$this->stamp}+{$this->amount}+{$this->reference}+{$this->message}+{$this->language}+{$this->merchant}+{$this->return}+{$this->cancel}+{$this->reject}+{$this->delayed}+{$this->country}+{$this->currency}+{$this->device}+{$this->content}+{$this->type}+{$this->algorithm}+{$this->delivery_date}+{$this->firstname}+{$this->familyname}+{$this->address}+{$this->postcode}+{$this->postoffice}+{$this->password}"));
    #        $post['VERSION']=$this->version;
    #        $post['STAMP']=$this->stamp;
    #        $post['AMOUNT']=$this->amount;
    #        $post['REFERENCE']=$this->reference;
    #        $post['MESSAGE']=$this->message;
    #        $post['LANGUAGE']=$this->language;
    #        $post['MERCHANT']=$this->merchant;
    #        $post['RETURN']=$this->return;
    #        $post['CANCEL']=$this->cancel;
    #        $post['REJECT']=$this->reject;
    #        $post['DELAYED']=$this->delayed;
    #        $post['COUNTRY']=$this->country;
    #        $post['CURRENCY']=$this->currency;
    #        $post['DEVICE']=$this->device;
    #        $post['CONTENT']=$this->content;
    #        $post['TYPE']=$this->type;
    #        $post['ALGORITHM']=$this->algorithm;
    #        $post['DELIVERY_DATE']=$this->delivery_date;
    #        $post['FIRSTNAME']=$this->firstname;
    #        $post['FAMILYNAME']=$this->familyname;
    #        $post['ADDRESS']=$this->address;
    #        $post['POSTCODE']=$this->postcode;
    #        $post['POSTOFFICE']=$this->postoffice;
    #        $post['MAC']=$mac;
    #
    #        if($this->device == 10){
    #            $post['EMAIL']=$this->email;
    #        }
    #        return $post;
    #    }

    # MD5(VERSION+ STAMP+ AMOUNT+ REFERENCE+ MESSAGE+ LANGUAGE+
    # MERCHANT+RETURN+CANCEL+REJECT+DELAYED+COUNTRY+CURRENCY+
    # DEVICE+CONTENT+TYPE+ALGORITHM+DELIVERY_DATE+FIRSTNAME+FAMILYNAME+
    # ADDRESS+POSTCODE+POSTOFFICE+turva-avain)

    #
    # $mac=strtoupper(md5("{$this->version}+{$this->stamp}+{$this->amount}+{$this->reference}+{$this->message}+
    # {$this->language}+{$this->merchant}+{$this->return}+
    # {$this->cancel}+{$this->reject}+{$this->delayed}+
    # {$this->country}+{$this->currency}+{$this->device}+{$this->content}+
    # {$this->type}+{$this->algorithm}+{$this->delivery_date}+
    # {$this->firstname}+{$this->familyname}+{$this->address}+
    # {$this->postcode}+{$this->postoffice}+{$this->password}"));

    o = odict()
    o["VERSION"] = "0001"
    o["STAMP"] = orderId

    # Format away decimal separator and such
    o["AMOUNT"] = str(int(get_required("AMOUNT")))

    # Bank accounting reference number
    o["REFERENCE"] = get_required("REFERENCE")

    # Bank accounting reference message
    o["MESSAGE"] = get_required("MESSAGE")
    o["LANGUAGE"] = "FI"
    o["MERCHANT"] = get_required("MERCHANT")
    o["RETURN"] = get_required("RETURN")
    o["CANCEL"] = get_required("CANCEL")

    # Not supported
    o["REJECT"] = ""
    o["DELAYED"] = ""

    # No foreign shopping support yet!
    o["COUNTRY"] = "FIN"
    o["CURRENCY"] = "EUR"

    # HTML
    o["DEVICE"] = "1"

    # This is not adult entertainment purchase
    o["CONTENT"] = "1"

    # No idea
    o["TYPE"] = "0"

    # No idea
    o['ALGORITHM']="2"

    o['DELIVERY_DATE']=get_required("DELIVERY_DATE")

    # Used for credit services
    o['FIRSTNANE'] = ""
    o['FAMILYNAME'] = ""
    o['ADDRESS'] = ""
    o['POSTCODE'] = ""
    o['POSTOFFICE'] = ""


    o["MAC"] = calculate_mac(secret, o)

    logger.warn("Mac:" + o["MAC"])

    return o

def confirm_payment_signature(secret, data):
    """
    Check that payment signature is right in
    HTTP POST coming from checkout.fi.

    @return True if signature matches

    ('STATUS', '2')
    ('ALGORITHM', '2')
    ('REFERENCE', '84')
    ('STAMP', '8')
    ('order-secret', '813279119')
    ('MAC', 'E8FB6D8243EE52FDFC65F134FF495792')
    ('VERSION', '0001')
    ('PAYMENT', '2665410')
    """

    # $generatedMac=strtoupper(md5("{$this->password}&{$this->version}&{$this->stamp}&{$this->reference}&{$this->payment}&{$this->status}&{$this->algorithm}"));
    o = odict()
    o["VERSION"] = data["VERSION"]
    o["STAMP"] = data["STAMP"]
    o["REFERENCE"] = data["REFERENCE"]
    o["PAYMENT"] = data["PAYMENT"]
    o["STATUS"] = data["STATUS"]
    o["ALGORITHM"] = data["ALGORITHM"]

    # 0001&35&354&2665785&2&2&SAIPPUAKAUPPIAS
    # 9D6C686F66D65E0956C8FB71E7A5FC93

    # 2012-02-23 11:29:58 WARNING checkout.fi Mac data:0001&34&385&2665800&2&2&SAIPPUAKAUPPIAS
    # 2012-02-23 11:29:58 WARNING checkout.fi Our mac:97B9AD07342948B1E89DE7D439565EC3
    # 2012-02-23 11:29:58 WARNING checkout.fi Incoming mac:2E8BEC4424E5128057D9A42FE7228BE6

    # Oh, why they need to use two different sepatators...?
    mac = calculate_mac(secret, o, separator="&", secret_at_end=False)

    logger.warn("Our mac:" + mac)
    logger.warn("Incoming mac:" + data["MAC"])

    return (mac == data["MAC"])
