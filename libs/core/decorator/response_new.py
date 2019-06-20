
import time
from functools import wraps
from django.db import transaction
from core.http.response import HttpResponse
from utils.log import logger
from utils.exceptions import PubErrorCustom,InnerErrorCustom
from core.paginator import Pagination
from django.core.serializers.json import DjangoJSONEncoder
from data import dictlist
from apps.user.models import Users
import json
from django.http import StreamingHttpResponse
import hashlib
from django.shortcuts import render
from django.template import loader
from apps.utils import url_join

class Core_connector:
    def __init__(self,**kwargs):
        self.transaction = kwargs.get('transaction',None)
        self.pagination = kwargs.get('pagination',None)
        self.serializer_class = kwargs.get('serializer_class',None)
        self.model_class = kwargs.get('model_class',None)
        self.lock = kwargs.get('lock',None)
        self.encryption =  kwargs.get('encryption',False)
        self.check_google_token = kwargs.get('check_google_token',None)
        self.is_file = kwargs.get('is_file',None)
        self.h5ValueHandler = None

    def __request_validate(self,request):

        logger.info("生成订单请求数据:{}".format(request.data))

        if not request.data.get("businessid"):
            raise PubErrorCustom('商户ID不能为空')

        try :
            request.user = Users.objects.get(userid=request.data.get("businessid"))
        except Users.DoesNotExist:
            raise PubErrorCustom("无效的商户!")

        if not request.data.get("businessid"):
            raise PubErrorCustom("商户ID为空!")
        if not request.data.get("paytypeid"):
            raise PubErrorCustom("支付方式为空!")
        if not request.data.get("down_ordercode"):
            raise PubErrorCustom("商户订单号为空!")
        if not request.data.get("client_ip"):
            raise PubErrorCustom("客户端IP为空!")
        if not request.data.get("amount"):
            raise PubErrorCustom("金额为空!")

        md5params = "{}{}{}{}{}{}{}".format(
            request.user.google_token,
            str(request.data.get("businessid")),
            str(request.data.get("paytypeid")),
            str(request.data.get("down_ordercode")),
            str(request.data.get("client_ip")),
            str(request.data.get("amount")),
            request.user.google_token)
        md5params = md5params.encode("utf-8")

        logger.info("待签数据:{}".format(md5params))
        sign = hashlib.md5(md5params).hexdigest()
        logger.info("签名:{}-----{}".format(sign,request.data.get("sign")))
        if sign != request.data.get("sign"):
            raise PubErrorCustom("验签失败!")


    def __run(self,func,outside_self,request,*args, **kwargs):

        if self.transaction:
            with transaction.atomic():
                res = func(outside_self, request, *args, **kwargs)
        else:
            res = func(outside_self, request, *args, **kwargs)

        if 'data' in res and 'res' in res['data'] and res['data']['res'] and 'htmlfile' in res['data'] and res['data']['htmlfile']:

            if str(res['data']['userid']) != '60':
                html = loader.render_to_string( res['data']['htmlfile'],  {
                    'data' : res['data']['res']
                }, request, using=None)
                print(html)
                with open('/var/html/tianyi/{}.html'.format( res['data']['ordercode']), 'w') as f1:
                    f1.write(html)
                return HttpResponse(data={"path" : url_join('/tianyi/{}.html').format(res['data']['ordercode'])}, headers=None, msg='操作成功!')
            else:
                if request.data.get("pass") == '1':
                    html = loader.render_to_string( res['data']['htmlfile'],  {
                        'data' : res['data']['res']
                    }, request, using=None)
                    # print(html)
                    # with open('/var/html/tianyi/{}.html'.format( res['data']['ordercode']), 'w') as f1:
                    #     f1.write(html)
                    return HttpResponse(data={"html" : html}, headers=None, msg='操作成功!')
                else:
                    return render(request, res['data']['htmlfile'],  {
                        'data' : res['data']['res']
                    })
        else:
            if not isinstance(res, dict):
                res = {'data': None, 'msg': None, 'header': None}
            if 'data' not in res:
                res['data'] = None
            if 'msg' not in res:
                res['msg'] =  {}
            if 'header' not in res:
                res['header'] = None
            logger.info("返回报文:{}".format(res['data']))
            return HttpResponse(data= res['data'],headers=res['header'], msg=res['msg'])

    def __response__validate(self,outside_self,func,response):
        logger.info('[%s : %s]Training complete in %lf real seconds' % (outside_self.__class__.__name__, getattr(func, '__name__'), self.end - self.start))

        return response

    def __call__(self,func):
        @wraps(func)
        def wrapper(outside_self,request,*args, **kwargs):
            try:
                self.start = time.time()
                self.__request_validate(request)
                response=self.__run(func,outside_self,request,*args, **kwargs)
                self.end=time.time()
                return response
            except PubErrorCustom as e:
                logger.error('[%s : %s  ] : [%s]'%(outside_self.__class__.__name__, getattr(func, '__name__'),e.msg))
                return HttpResponse(success=False, msg=e.msg, data=None)
            except InnerErrorCustom as e:
                logger.error('[%s : %s  ] : [%s]'%(outside_self.__class__.__name__, getattr(func, '__name__'),e.msg))
                return HttpResponse(success=False, msg=e.msg, rescode=e.code, data=None)
            except Exception as e:
                logger.error('[%s : %s  ] : [%s]'%(outside_self.__class__.__name__, getattr(func, '__name__'),str(e)))
                return HttpResponse(success=False, msg=str(e), data=None)
        return wrapper