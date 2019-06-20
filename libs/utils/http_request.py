

from requests import request

from utils.log import logger


def get_token(request):
    return request.META.get('HTTP_AUTHORIZATION')


# def send_request(url, token, params=None):
#     try:
#         result = requests.get(url, headers={'Authorization': token}, params=params)
#         status_code = result.status_code
#         result = result.json()
#         if result.get('rescode') == '10000':
#             return True, result.get('data')
#         return False, None
#     except Exception as ex:
#         logger.error('{0} 调用失败:{1}'.format(url, ex))
#         return False, None


def send_request(url, token=None, method='get', params=None, data=None ,headers={}):
    logger.info("请求参数: url:{} header:{} body:{}".format(url,headers,data))
    try:
        result = request(method, url, params=params, json =data, verify=False,headers=headers)
        status_code = result.status_code
        result = result.json()
        logger.info(result)
        # logger.info("status_code:", status_code)
        # logger.info("result:" ,result)
        if str(result.get('rescode')) == '10000' or str(result.get('rspcode')) == '10000':
            return True, result.get('data') if 'data' in result else {}
        return False, result.get('msg')
    except Exception as ex:
        logger.error('{0} 调用失败:{1}'.format(url, ex))
        return False, '{0}'.format(ex)
