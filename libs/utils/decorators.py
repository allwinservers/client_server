# coding:utf-8
from functools import wraps

from utils.http import APIResponse, APIResponseNotFound


def request_validate(serializer_class, model_class=None):
    '''通用请求参数处理'''

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            pk = kwargs.get('pk')
            instance = None
            if pk:
                try:
                    instance = model_class.objects.get(pk=pk)
                except TypeError:
                    return APIResponse(success=False, msg='serializer_class类型错误')
                except Exception as ex:
                    return APIResponseNotFound(msg='未找到')
            serializer = serializer_class(data=request.data, instance=instance, user=request.user, request=request)
            if not serializer.is_valid():
                errors = [key + ':' + value[0] for key, value in serializer.errors.items() if isinstance(value, list)]
                if errors:
                    error = errors[0]
                    error = error.lstrip(':')
                else:
                    for key, value in serializer.errors.items():
                        if isinstance(value, dict):
                            key, value = value.popitem()
                            error = key + ':' + value[0]
                            break
                return APIResponse(success=False, msg=error)
            kwargs['serializer'] = serializer
            kwargs['instance'] = instance
            return view_func(self, request, *args, **kwargs)

        return wrapper

    return decorator
