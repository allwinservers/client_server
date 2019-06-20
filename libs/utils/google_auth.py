

import pyotp

def create_google_token():
    return pyotp.random_base32()

def check_google_token(gtoken,vercode):
    return True if str(pyotp.TOTP(gtoken).now()) == str(vercode) else False
