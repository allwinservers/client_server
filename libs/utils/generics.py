from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404 as _get_object_or_404
from rest_framework import exceptions

from utils.string_extension import safe_int


def is_owner_or_404(request, user_id):
    """
    校验登录用户是否是资源所有者
    :param request:
    :param user_id:
    :return:
    """
    if request.user.id != safe_int(user_id):
        raise exceptions.NotFound


def get_object_or_404(queryset, *filter_args, **filter_kwargs):
    """
    Same as Django's standard shortcut, but make sure to also raise 404
    if the filter_kwargs don't match the required types.
    """
    try:
        return _get_object_or_404(queryset, *filter_args, **filter_kwargs)
    except (TypeError, ValueError, ValidationError):
        raise exceptions.NotFound
