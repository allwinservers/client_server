"""JSON helper functions"""
import json

from django.core.exceptions import ValidationError
from rest_framework.response import Response

from .response import res_code, res

CONTENT_RANGE = 'X-Content-Range'
CONTENT_TOTAL = 'X-Content-Total'

LIMIT = 50


def get_limit(limit):
    return LIMIT if limit > LIMIT else limit


class APIResponse(Response):
    status_code = 200

    def __init__(self, rescode=res_code['success'], success=True, data=None, msg=''):
        '''
        rescode与success参数只需传入其中任意一个。传入success，则状态码为全局成功\错误状态码；传入rescode，为自定义错误状态码
        :param rescode: 状态码
        :param success: 是否成功
        :param data: 输出数据
        :param msg: 提示信息
        '''
        if self.status_code != 200:
            success = False

        if rescode != res_code['success']:
            res['rescode'] = rescode
            res['msg'] = msg if msg else '请求出错,请稍后再试！'
        else:
            if success:
                res['rescode'] = res_code['success']
                res['msg'] = msg if msg else '操作成功'
            else:
                res['rescode'] = res_code['error']
                res['msg'] = msg if msg else '请求出错,请稍后再试！'
        res['data'] = data
        super().__init__(res)


class APIResponseBadRequest(APIResponse):
    status_code = 400


class APIResponseUnauthorized(APIResponse):
    status_code = 401


class APIResponseForbidden(APIResponse):
    status_code = 403


class APIResponseNotFound(APIResponse):
    status_code = 404


class APIResponseNotAllowed(APIResponse):
    status_code = 405


class APIResponseNotAcceptable(APIResponse):
    status_code = 406


class APIResponseException(APIResponse):
    status_code = 500


http_response = {
    200: APIResponse,
    400: APIResponseBadRequest,
    401: APIResponseUnauthorized,
    403: APIResponseForbidden,
    404: APIResponseNotFound,
    405: APIResponseNotAllowed,
    406: APIResponseNotAcceptable,
    500: APIResponseException
}
