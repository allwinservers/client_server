
from apps.user.models import Users

def check_passwd(userid,passwd):
    if not Users.objects.filter(userid=userid,passwd=passwd).exists():
        return False
    return True

def check_pay_passwd(userid,passwd):
    if not Users.objects.filter(userid=userid,pay_passwd=passwd).exists():
        return False
    return True


