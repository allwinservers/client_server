from django.conf import settings

from utils.http_request import send_request


USER_API_HOST = settings.USER_API_HOST
SUPPLIER_API = USER_API_HOST + '/service/suppliers/all'
OPERATOR_API = USER_API_HOST + '/service/operators/all'


def get_creator_id(request, username):
    if username:
        token = request.META.get('HTTP_AUTHORIZATION')
        is_success, data = send_request(OPERATOR_API, token, params={'username': username})
        if is_success:
            return [item['id'] for item in data]
        return []


def get_supplier_id(request, company):
    if company:
        token = request.META.get('HTTP_AUTHORIZATION')
        is_success, data = send_request(SUPPLIER_API, token, params={'company': company})
        if is_success:
            return [item['id'] for item in data]
        return []

