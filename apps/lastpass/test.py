from cryptokit import AESCrypto
import base64
import json
import demjson
from libs.utils.google_auth import create_google_token
import binascii
import os


# # key="4S4G7CBWJHYAD5ZE"
# s=create_google_token()
# print(s)
key="NE76TRFQFMYSVRMQ"
def encrypt(word):
    crypto = AESCrypto(key,key)
    data = crypto.encrypt(word,mode='cbc')
    return base64.b64encode(data)

def decrypt(word):
    word=word.encode('utf-8')
    crypto = AESCrypto(key,key)
    data=base64.b64decode(word)
    return crypto.decrypt(data)
s=decrypt("zCRqGO87HLYWDQtSEcPaZ0CXp6j9itLIQLvkMkF494BTfPk+Nr0zmUBdMGtyNW433X40bu0Cjh1U27XQzzyTIQ==")

print(s)
#print(encrypt('{"down_ordercode":"W19060410401505950490841","amount":"10.00","createtime":"20190604104018","client_ip":"127.0.0.1","notifyurl":"http://19ad14b8.ngrok.io/aoyin/Notify","ismobile":"1"}')
#value=json.dumps({"userid":1,"amount":100.1 })
#print(encrypt(value))
#print(encrypt('{"page":2,"page_size":10}'))
#print(demjson.decode(decrypt('NYGPLEEmXyZLIEGwXhXm5wMIoIPjYYWE5oa08IEBBn86/T4QV4e//FXWc3b62jHCu2q3NAgYnWk4cwPrmOnR0VHDf7yNJVPoz6LQpKPG+B/vNishD9u036m9PMTAEsZKz2s87cgRX1BeqlRL/ZQlvp+04/eI8c9t/G6tiImBLx4=')))
#print(demjson.decode(decrypt('NYGPLEEmXyZLIEGwXhXm5wMIoIPjYYWE5oa08IEBBn86/T4QV4e//FXWc3b62jHCu2q3NAgYnWk4cwPrmOnR0VHDf7yNJVPoz6LQpKPG B/vNishD9u036m9PMTAEsZKz2s87cgRX1BeqlRL/ZQlvp 04/eI8c9t/G6tiImBLx4=')))
# print(encrypt("hello word"))

# print(encrypt('{"data":{"name":"张飞"}}'))
#
#
import demjson
import urllib
import requests
#
# keep_info="""
# {'down_ordercode': '112441532', 'amount': '500', 'createTime': '1558602519075', 'paytypeid': '1', 'notifyurl': 'http://allwin6666.com/api/paycall/wechat_test?allwin_test=1', 'client_ip': '127.0.0.1', 'ismobile': '1', 'createtime': 1558602520.0}
# """
# s=demjson.decode(keep_info)
#
#
# print(urllib.parse.quote('allwin6666.com/api/business/get_paytype?data=lM+Xl9vHlw/0IO05M/FEEjTYARnmaR65cB9Oew9GBR8='))
#
# requests.get(url='allwin6666.com/api/business/get_paytype',headers={
#     "token":"19,N2NZW2LG3NBK65IT"
# },params={
#     "data" : urllib.parse.quote('lM+Xl9vHlw/0IO05M/FEEjTYARnmaR65cB9Oew9GBR8=')
# })


# a=b'mHtklJaYjdf69T1kd+zlqr5hRrywu1aBzPEw3xItt7CT9sLsM+9KTlB0KxvpAtCYqdhtSwQYK/S/umqzGi7rcYjUdL1vhYSOx4sLLiIqBDZUyJAdpf+pOh/yPSYDZrTgfpTR/FZeiXzloTmBxa8oG7kn2L9fIG4eelqDpfE4eArtIlBkZUSLIvXQLx7sJ8Wg3yLjTxo1P3rk06sOJcWmkVoTzlmnzrWdhMxUHALpkBbOt2SG5G7IeGdZNFdyOSYllAjeHlwez7T7GGzjohYxLj+Cy0UgWZN53cDFy/UVxT+I3Kf3y7An+RdpLDI4iVcbXzugWycMxxDy2QgpUHM8TMTqCBRXgE88F7xGXWYvpMMpUURP4ty07hC6uD5lPD14APLLZ5teMjPuxWe2l8px8Qu7U/AVROhGQp2RiWmA2itNHHESxb2XN/IApBuA0bEqbcJKDIrcV5Sv3/1BqSZiDw=='
#
# print(a.decode('utf-8'))