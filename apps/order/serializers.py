

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from apps.order.models import Order,CashoutList,UpCashoutList
from libs.utils.mytime import timestamp_toTime
from apps.user.models import Users
from include.data.choices_list import Choices_to_Dict

class OrderModelSerializer1(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = '__all__'

class OrderModelSerializer(serializers.ModelSerializer):

    status_name = serializers.SerializerMethodField()
    down_status_name = serializers.SerializerMethodField()
    createtime = serializers.SerializerMethodField()

    amount = serializers.DecimalField(max_digits=18,decimal_places=2)
    confirm_amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    tech_cost = serializers.DecimalField(max_digits=18, decimal_places=2)
    myfee = serializers.DecimalField(max_digits=18, decimal_places=2)
    codefee = serializers.DecimalField(max_digits=18, decimal_places=2)

    no = serializers.SerializerMethodField()

    username = serializers.SerializerMethodField()

    def get_username(self,obj):
        return Users.objects.get(userid=obj.userid).name

    def get_no(self,obj):
        return obj.down_ordercode

    def get_status_name(self,obj):
        return Choices_to_Dict('order_status')[obj.status]

    def get_down_status_name(self,obj):
        return Choices_to_Dict('order_down_status')[obj.down_status]

    def get_createtime(self,obj):
        return timestamp_toTime(obj.createtime) if obj.createtime else ""

    class Meta:
        model = Order
        fields = '__all__'


class CashoutListModelSerializer(serializers.ModelSerializer):

    status_name = serializers.SerializerMethodField()
    createtime = serializers.SerializerMethodField()

    updtime = serializers.SerializerMethodField()

    def get_status_name(self,obj):
        if obj.status == "0" :
            return '提现申请中'
        elif obj.status == "1":
            return '打款成功'
        else:
            return '打款已拒绝'

    def get_createtime(self,obj):
        if obj.createtime:
            return timestamp_toTime(obj.createtime)
        else:
            return ""

    def get_updtime(self,obj):
        if obj.updtime:
            return timestamp_toTime(obj.updtime)
        else:
            return ""

    class Meta:
        model = CashoutList
        fields = '__all__'

class UpCashoutListModelSerializer(serializers.ModelSerializer):

    status_name = serializers.SerializerMethodField()
    createtime = serializers.SerializerMethodField()

    updtime = serializers.SerializerMethodField()

    def get_status_name(self, obj):
        if obj.status == "0":
            return '提现申请中'
        elif obj.status == "1":
            return '打款成功'
        else:
            return '打款已拒绝'

    def get_createtime(self, obj):
        if obj.createtime:
            return timestamp_toTime(obj.createtime)
        else:
            return ""

    def get_updtime(self, obj):
        if obj.updtime:
            return timestamp_toTime(obj.updtime)
        else:
            return ""

    class Meta:
        model = UpCashoutList
        fields = '__all__'