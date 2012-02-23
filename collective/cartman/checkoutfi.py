"""

    Checkout.fi payment service implementation in Python

    http://checkout.fi/ohjelmistopaketit.html

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

def construct_checkout(orderId, secret, data):
    """

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
    o["REFERENCE"] = create_reference_number(orderId)

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
    o['ALGORITHM']="1"

    o['DELIVERY_DATE']=get_required("DELIVERY_DATE")

    # Used for credit services
    o['FIRSTNANE'] = ""
    o['FAMILYNAME'] = ""
    o['ADDRESS'] = ""
    o['POSTCODE'] = ""
    o['POSTOFFICE'] = ""

    # calculate MAC
    concat = "".join(o.values())

    logger.warn(o)
    logger.warn(concat)

    if not secret:
        raise RuntimeError("Missing shared secret")

    concat += secret

    m = hashlib.md5()
    m.update(concat)

    o["MAC"] = m.hexdigest().upper()

    return o


