

from libs.utils.redlock import ReadLock
from utils.exceptions import PubErrorCustom



def redisLock(resource,msg=None):
    with ReadLock(resource=resource) as Lock:
        if not Lock:
            if msg:
                raise PubErrorCustom(msg)
            else:
                raise PubErrorCustom("正在进行处理,请稍等!")

def redisLockLoop(resource):
    isFlag = True

    while isFlag :
        with ReadLock(resource=resource) as Lock:
            if Lock:
                isFlag = False