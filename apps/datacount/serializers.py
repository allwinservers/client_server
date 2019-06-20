

from rest_framework import serializers
from apps.datacount.models import OrderCount

class OrderCountModelSerializer(serializers.ModelSerializer):

    today_rate = serializers.SerializerMethodField()
    today_amount = serializers.DecimalField(max_digits=18, decimal_places=2)

    def get_today_rate(self,obj):

        return "{}%".format(round(float(obj.today_rate) * 100.0,2))

    class Meta:
        model = OrderCount
        fields = '__all__'