from apps.utils import GenericViewSetCustom
from rest_framework.decorators import list_route

from core.decorator.response import Core_connector

from utils.exceptions import PubErrorCustom,InnerErrorCustom

from apps.business.serializers import PayTypeBusinessSerializer

from apps.pay.models import PayType,PayPassLinkType

from include.data.redislockkey import BUSINESS_CREATE_OREDER

from apps.business.utils import CreateOrder


class BusinessAPIView(GenericViewSetCustom):

    @list_route(methods=['GET'])
    @Core_connector(pagination=True,check_google_token=True)
    def get_paytype(self, request, *args, **kwargs):

        paypass = PayPassLinkType.objects.raw(
            """
            SELECT t1.*,t2.typename ,t2.name as paytypename FROM paypasslinktype as t1 
            INNER JOIN paytype as t2 on t1.paytypeid = t2.paytypeid
            WHERE t1.to_id=%s and t1.type='1' 
            """,[request.user.userid]
        )
        data = []
        for item in paypass:
            data.append({
                "paytypeid" : item.paytypeid,
                "name" : item.typename + item.paytypename
            })

        if not len(data):
            raise PubErrorCustom("请联系客服设置支付方式!")
        return {"data" :  data}

    @list_route(methods=['POST'])
    @Core_connector(transaction=True,check_google_token=True)
    def create_order(self, request, *args, **kwargs):
        return {"data": CreateOrder(user=request.user,request_param=self.request.data_format).run()}