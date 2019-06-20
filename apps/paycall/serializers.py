

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from apps.paycall.models import FlmTranList
from libs.utils.mytime import timestamp_toTime

class FlmTranListModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = FlmTranList
        fields = '__all__'
