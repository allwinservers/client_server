

import pyotp

def create_google_token():
    return pyotp.random_base32()

def check_google_token(gtoken,vercode):
    return True if str(pyotp.TOTP(gtoken).now()) == str(vercode) else False

def create_google_token_url(gtoken,name):
    return pyotp.totp.TOTP(gtoken).provisioning_uri("alice@google.com",  issuer_name="傲银支付({})".format(name))


if __name__ == '__main__':
    res = pyotp.totp.TOTP('4S4G7CBWJHYAD5ZE').provisioning_uri("alice@google.com",  issuer_name="傲银支付")

    print(res)

    print(check_google_token("4S4G7CBWJHYAD5ZE",255788))