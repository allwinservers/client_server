


from rest_framework import serializers
from apps.pay.models import PayType

class PayTypeBusinessSerializer(serializers.Serializer):

    paytypeid = serializers.IntegerField()
    name = serializers.SerializerMethodField()

    def get_name(self,obj):
        return obj.typename + obj.name