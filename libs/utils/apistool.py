
from utils.exceptions import PubErrorCustom
from data import dictlist



def SaveSerializer(serializers_class=None,instance=None,data=None):
    serializer=serializers_class(instance=instance,data=data)

    if not serializer.is_valid():
        errors = [key + ':' + value[0] for key, value in serializer.errors.items() if
                  isinstance(value, list)]
        if errors:
            error = errors[0]
            error = error.lstrip(':').split(':')
            try:
                error = "{}:{}".format(getattr(dictlist, error[0]), error[1])
            except AttributeError as e:
                error = error[1]
        else:
            for key, value in serializer.errors.items():
                if isinstance(value, dict):
                    key, value = value.popitem()
                    error = key + ':' + value[0]
                    break
        raise PubErrorCustom(error)
    value = serializer.save()
    return value