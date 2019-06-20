from apps.utils import GenericViewSetCustom
from rest_framework.decorators import list_route

from core.decorator.response_new import Core_connector

from apps.business.utils import CreateOrder


class BusinessNewAPIView(GenericViewSetCustom):

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def create_order(self, request, *args, **kwargs):

        data={}
        for item in request.data:
            data[item] = request.data[item]
        return {"data":CreateOrder(user=request.user, request_param=data, lock="1").run()}


    # @list_route(methods=['GET'])
    # @Core_connector(transaction=True)
    # def create_order_get(self, request, *args, **kwargs):
    #     data={}
    #     for item in request.data:
    #         data[item] = request.data[item]
    #     return {"data":CreateOrder(user=request.user, request_param=data, lock="1").run()}