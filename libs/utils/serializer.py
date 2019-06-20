import time
from urllib.parse import urljoin

from django.conf import settings
from rest_framework import serializers


class BaseRepresentationSerializer:
    def __init__(self, data, many=False, **kwargs):
        self.initial_data = data
        self.context = kwargs.pop('context', {})
        self.many = many

    def to_representation(self, data, instance):
        pass

    @property
    def data(self):
        pass


def timestamp_field(value):
    return int(time.mktime(value.timetuple()))


def url_field(host, value):
    if value:
        return host + value
    return value


class TimestampField(serializers.Field):
    def to_representation(self, value):
        return int(time.mktime(value.timetuple()))


class UrlListField(serializers.ListField):
    child = serializers.CharField(required=False)

    def to_representation(self, data):
        if data:
            urls = []
            for item in data.split(','):
                urls.append(urljoin(settings.QINIU_HOST, item))
            return urls
        return []


class UrlField(serializers.CharField):

    def to_representation(self, value):
        value = super().to_representation(value)
        if value:
            return urljoin(settings.QINIU_HOST, value)
        return value


class BaseSerializer:
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
