


from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from apps.pay.models import PayType,PayPass,PayPassLinkType,BankInfo
from libs.utils.mytime import timestamp_toTime

from libs.utils.mytime import UtilTime

# class WeiboPayUsernameModelSerializer(serializers.ModelSerializer):
#
#     createtime_format = serializers.SerializerMethodField()
#     logintime_format = serializers.SerializerMethodField()
#     status_format = serializers.SerializerMethodField()
#     type_format = serializers.SerializerMethodField()
#
#     def get_createtime_format(self,obj):
#         return UtilTime().timestamp_to_string(obj.createtime)
#
#     def get_logintime_format(self,obj):
#         return UtilTime().timestamp_to_string(obj.logintime)
#
#     def get_status_format(self,obj):
#         return "是" if obj.status=='0' else '否'
#
#     def get_type_format(self,obj):
#         return "发红包" if obj.type=='0' else '抢红包'
#
#     class Meta:
#         model = WeiboPayUsername
#         fields = '__all__'

class PayTypeModelSerializer(serializers.ModelSerializer):

    rate = serializers.DecimalField(max_digits=18,decimal_places=4)
    passid = serializers.IntegerField()
    paypassname = serializers.CharField()
    userid = serializers.CharField()

    class Meta:
        model = PayType
        fields = '__all__'

class PayTypeModelSerializer1(serializers.ModelSerializer):

    class Meta:
        model = PayType
        fields = '__all__'

class PayPassModelSerializer(serializers.ModelSerializer):


    createtime_format = serializers.SerializerMethodField()
    status_format = serializers.SerializerMethodField()
    isdayfu_format = serializers.SerializerMethodField()
    custom_format = serializers.SerializerMethodField()

    def get_createtime_format(self,obj):
        return UtilTime().timestamp_to_string(obj.createtime)

    def get_status_format(self,obj):
        return "是" if obj.status=='0' else '否'

    def get_isdayfu_format(self,obj):
        return "是" if obj.isdayfu=='0' else '否'

    def get_custom_format(self,obj):
        return "自定义" if obj.custom=='0' else '规则'


    class Meta:
        model = PayPass
        fields = '__all__'

class PayPassLinkTypeModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayPassLinkType
        fields = '__all__'

        validators = [
            UniqueTogetherValidator(
                queryset=PayPassLinkType.objects.all(),
                fields=('paytypeid','to_id','type','userid',),
                message="关联关系重复！"
            ),
        ]

class RateSerializer(serializers.Serializer):

    typename = serializers.CharField()
    paytypename = serializers.CharField()
    rate = serializers.DecimalField(max_digits=18,decimal_places=4)


class BankInfoModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankInfo
        fields = '__all__'