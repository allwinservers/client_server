
from utils.log import logger
from core.http.response import res_code, ResCode
from apps.user.models import Users,Token,Role


def get_user(request):
    """
    Return the user model instance associated with the given request session.
    If no user is retrieved, return an instance of `AnonymousUser`.
    """

    token = request.META.get('HTTP_AUTHORIZATION')
    if not token:
        return (None,'token不存在,请退出后重新登录！', 200, ResCode.Token_Missing)

    try:
        result=Token.objects.get(key=token)
    except Token.DoesNotExist:
        return (None,'token已失效,请退出后重新登录！', 200, ResCode.Token_Missing)

    user=Users.objects.get(userid=result.userid)
    user.rolename = Role.objects.get(rolecode=user.rolecode).name
    if user.status == 1:
        return (None, '登录账号不存在!',200, ResCode.Token_Missing)
    elif user.status == 2:
        return (None, '已冻结！', 200, ResCode.Token_Missing)

    return (user,'操作成功！', 200, ResCode.Success)
