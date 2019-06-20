


from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from apps.pay.models import PayType,PayPass,PayPassLinkType,BankInfo
from libs.utils.mytime import timestamp_toTime

class PayTypeModelSerializer(serializers.ModelSerializer):

    rate = serializers.DecimalField(max_digits=18,decimal_places=4)
    passid = serializers.IntegerField()
    paypassname = serializers.CharField()

    class Meta:
        model = PayType
        fields = '__all__'

class PayTypeModelSerializer1(serializers.ModelSerializer):

    class Meta:
        model = PayType
        fields = '__all__'

class PayPassModelSerializer(serializers.ModelSerializer):


    bal = serializers.DecimalField(max_digits=18,decimal_places=2)

    status_name = serializers.SerializerMethodField()


    def get_status_name(self,obj):
        if str(obj.status) == '0':
            return '启用'
        elif str(obj.status) == '1':
            return '不启用'
        elif str(obj.status) == '2':
            return '删除'

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
                fields=('paytypeid','to_id','type',),
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