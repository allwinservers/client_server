"""
Provides various authentication policies.
"""
from __future__ import unicode_literals

from core.http.response import HttpResponse1
from rest_framework.authentication import BaseAuthentication

from auth import get_user

class Authentication(BaseAuthentication):
    def authenticate(self, request):
        request.user, msg, status_code, rescode = get_user(request)

        detail = {
            'rescode': rescode,
            'msg': msg,
            'status_code': status_code
        }
        if rescode != '10000':
            raise HttpResponse1(detail)
        return (request.user, None)