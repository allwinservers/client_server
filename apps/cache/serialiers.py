
from rest_framework import serializers

from apps.public.models import WhiteList


class WhiteListModelSerializerToRedis(serializers.ModelSerializer):

    class Meta:
        model = WhiteList
        fields = '__all__'

