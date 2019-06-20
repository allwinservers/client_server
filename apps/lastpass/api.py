

from apps.utils import GenericViewSetCustom
from rest_framework.decorators import list_route
from core.decorator.response import Core_connector
from utils.exceptions import PubErrorCustom,InnerErrorCustom
from utils.log import logger
from apps.lastpass.utils import LastPass_JLF,LastPass_TY,LastPass_DD,LastPass_YZL,LastPass_OSB,LastPass_BAOZHUANKA,LastPass_LIMAFU,LastPass_JUXING,LastPass_MK,LastPass_TONGYU

from rest_framework.response import Response
from django.db import transaction
from functools import wraps
import json
from django.shortcuts import HttpResponse

class Jl_HttpResponse(Response):

    def __init__(self,data=None):
        super().__init__(data=data)

class Jl_Core_connector:
    def __init__(self,**kwargs):
        pass
    def __run(self,func,outside_self,request,*args, **kwargs):
        with transaction.atomic():
            res = func(outside_self, request, *args, **kwargs)

    def __call__(self,func):
        @wraps(func)
        def wrapper(outside_self,request,*args, **kwargs):
            try:
                self.__run(func,outside_self,request,*args, **kwargs)
                return HttpResponse("success")
            except PubErrorCustom as e:
                logger.error('[%s : %s  ] : [%s]'%(outside_self.__class__.__name__, getattr(func, '__name__'),e.msg))
                return HttpResponse("fail")
            except Exception as e:
                logger.error('[%s : %s  ] : [%s]'%(outside_self.__class__.__name__, getattr(func, '__name__'),str(e)))
                return HttpResponse("fail")
        return wrapper

class Ty_Core_connector:
    def __init__(self,**kwargs):
        pass
    def __run(self,func,outside_self,request,*args, **kwargs):
        with transaction.atomic():
            res = func(outside_self, request, *args, **kwargs)

    def __call__(self,func):
        @wraps(func)
        def wrapper(outside_self,request,*args, **kwargs):
            try:
                self.__run(func,outside_self,request,*args, **kwargs)
                return HttpResponse("OK")
            except PubErrorCustom as e:
                logger.error('[%s : %s  ] : [%s]'%(outside_self.__class__.__name__, getattr(func, '__name__'),e.msg))
                return HttpResponse("fail")
            except Exception as e:
                logger.error('[%s : %s  ] : [%s]'%(outside_self.__class__.__name__, getattr(func, '__name__'),str(e)))
                return HttpResponse("fail")
        return wrapper

class Yzl_Core_connector:
    def __init__(self,**kwargs):
        pass
    def __run(self,func,outside_self,request,*args, **kwargs):
        with transaction.atomic():
            res = func(outside_self, request, *args, **kwargs)

    def __call__(self,func):
        @wraps(func)
        def wrapper(outside_self,request,*args, **kwargs):
            try:
                self.__run(func,outside_self,request,*args, **kwargs)
                return HttpResponse("success")
            except PubErrorCustom as e:
                logger.error('[%s : %s  ] : [%s]'%(outside_self.__class__.__name__, getattr(func, '__name__'),e.msg))
                return HttpResponse("fail")
            except Exception as e:
                logger.error('[%s : %s  ] : [%s]'%(outside_self.__class__.__name__, getattr(func, '__name__'),str(e)))
                return HttpResponse("fail")
        return wrapper


class OSB_Core_connector:
    def __init__(self,**kwargs):
        pass
    def __run(self,func,outside_self,request,*args, **kwargs):
        with transaction.atomic():
            res = func(outside_self, request, *args, **kwargs)

    def __call__(self,func):
        @wraps(func)
        def wrapper(outside_self,request,*args, **kwargs):
            try:
                self.__run(func,outside_self,request,*args, **kwargs)
                return HttpResponse("success")
            except PubErrorCustom as e:
                logger.error('[%s : %s  ] : [%s]'%(outside_self.__class__.__name__, getattr(func, '__name__'),e.msg))
                return HttpResponse("fail")
            except Exception as e:
                logger.error('[%s : %s  ] : [%s]'%(outside_self.__class__.__name__, getattr(func, '__name__'),str(e)))
                return HttpResponse("fail")
        return wrapper

class BAOZHUANKA_Core_connector:
    def __init__(self,**kwargs):
        pass
    def __run(self,func,outside_self,request,*args, **kwargs):
        with transaction.atomic():
            res = func(outside_self, request, *args, **kwargs)

    def __call__(self,func):
        @wraps(func)
        def wrapper(outside_self,request,*args, **kwargs):
            try:
                self.__run(func,outside_self,request,*args, **kwargs)
                return HttpResponse("ok")
            except PubErrorCustom as e:
                logger.error('[%s : %s  ] : [%s]'%(outside_self.__class__.__name__, getattr(func, '__name__'),e.msg))
                return HttpResponse("fail")
            except Exception as e:
                logger.error('[%s : %s  ] : [%s]'%(outside_self.__class__.__name__, getattr(func, '__name__'),str(e)))
                return HttpResponse("fail")
        return wrapper

class JUXING_Core_connector:
    def __init__(self,**kwargs):
        pass
    def __run(self,func,outside_self,request,*args, **kwargs):
        with transaction.atomic():
            res = func(outside_self, request, *args, **kwargs)

    def __call__(self,func):
        @wraps(func)
        def wrapper(outside_self,request,*args, **kwargs):
            try:
                self.__run(func,outside_self,request,*args, **kwargs)
                return HttpResponse("success")
            except PubErrorCustom as e:
                logger.error('[%s : %s  ] : [%s]'%(outside_self.__class__.__name__, getattr(func, '__name__'),e.msg))
                return HttpResponse("fail")
            except Exception as e:
                logger.error('[%s : %s  ] : [%s]'%(outside_self.__class__.__name__, getattr(func, '__name__'),str(e)))
                return HttpResponse("fail")
        return wrapper

class Lmf_Core_connector:
    def __init__(self,**kwargs):
        pass
    def __run(self,func,outside_self,request,*args, **kwargs):
        with transaction.atomic():
            res = func(outside_self, request, *args, **kwargs)

    def __call__(self,func):
        @wraps(func)
        def wrapper(outside_self,request,*args, **kwargs):
            try:
                self.__run(func,outside_self,request,*args, **kwargs)
                return HttpResponse("SUCCESS")
            except PubErrorCustom as e:
                logger.error('[%s : %s  ] : [%s]'%(outside_self.__class__.__name__, getattr(func, '__name__'),e.msg))
                return HttpResponse("fail")
            except Exception as e:
                logger.error('[%s : %s  ] : [%s]'%(outside_self.__class__.__name__, getattr(func, '__name__'),str(e)))
                return HttpResponse("fail")
        return wrapper

class LastPassAPIView(GenericViewSetCustom):

    @list_route(methods=['POST'])
    @Jl_Core_connector()
    def juli_callback(self, request, *args, **kwargs):
        data={}
        for item in request.data:
            data[item] = request.data[item]
        LastPass_JLF(data=data).call_run()
        return None

    @list_route(methods=['POST'])
    @Ty_Core_connector()
    def tianyi_callback(self, request, *args, **kwargs):
        data={}
        for item in request.data:
            data[item] = request.data[item]
        LastPass_TY(data=data).call_run()
        return None


    @list_route(methods=['POST'])
    @Ty_Core_connector()
    def mk_callback(self, request, *args, **kwargs):
        data={}
        for item in request.data:
            data[item] = request.data[item]
        LastPass_MK(data=data).call_run()
        return None

    @list_route(methods=['POST'])
    @Lmf_Core_connector()
    def tongyu_callback(self, request, *args, **kwargs):
        data={}
        for item in request.data:
            data[item] = request.data[item]
        data1={}
        for item in data:
            data1=json.loads(item)
        data={}
        for item in data1:
            data[item] = data1[item]
        LastPass_TONGYU(data=data).call_run()
        return None

    @list_route(methods=['POST'])
    @Ty_Core_connector()
    def dada_callback(self, request, *args, **kwargs):
        data={}
        for item in request.data:
            data[item] = request.data[item]
        LastPass_DD(data=data).call_run()
        return None

    @list_route(methods=['POST'])
    @Yzl_Core_connector()
    def yzl_callback(self, request, *args, **kwargs):
        data={}
        for item in request.data:
            data[item] = request.data[item]
        LastPass_YZL(data=data).call_run()
        return None

    @list_route(methods=['POST'])
    @OSB_Core_connector()
    def osb_callback(self, request, *args, **kwargs):
        data={}
        for item in request.data:
            data[item] = request.data[item]
        LastPass_OSB(data=data).call_run()
        return None

    @list_route(methods=['POST'])
    @BAOZHUANKA_Core_connector()
    def baozhanka_callback(self, request, *args, **kwargs):
        data={}
        for item in request.data:
            data[item] = request.data[item]
        LastPass_BAOZHUANKA(data=data).call_run()
        return None

    @list_route(methods=['GET'])
    @Lmf_Core_connector()
    def limafu_callback(self, request, *args, **kwargs):
        data={}
        for item in request.query_params:
            data[item] = request.query_params[item]
        LastPass_LIMAFU(data=data).call_run()
        return None

    @list_route(methods=['POST'])
    @JUXING_Core_connector()
    def juxing_callback(self, request, *args, **kwargs):
        data={}
        for item in request.data:
            data[item] = request.data[item]
        LastPass_JUXING(data=data).call_run()
        return None

    @list_route(methods=['GET'])
    @Jl_Core_connector()
    def juli_callback_test(self, request, *args, **kwargs):
        return None

    @list_route(methods=['GET'])
    @Jl_Core_connector()
    def tianyi_callback_test(self, request, *args, **kwargs):
        return None