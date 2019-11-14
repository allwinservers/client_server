import binasciiimport osfrom rest_framework import viewsetsfrom rest_framework.decorators import list_routefrom core.decorator.response import Core_connectorfrom utils.exceptions import PubErrorCustomfrom apps.user.serializers import UsersSerializer1from apps.user.models import Users,Login,Tokenfrom django.shortcuts import HttpResponsefrom apps.utils import RedisHandlerclass UserAPIView(viewsets.ViewSet):    @list_route(methods=['POST'])    @Core_connector(transaction=True,serializer_class=UsersSerializer1,model_class=Users)    def register(self, request,*args,**kwargs):        serializer = kwargs.pop('serializer')        isinstance=serializer.save()        isinstance.status=1        isinstance.save()        return {"msg":"添加成功！"}    @list_route(methods=['POST'])    @Core_connector(transaction=True)    def login(self, request, *args, **kwargs):        userlogin=Login()        try:            user = Users.objects.get(loginname=request.data_format.get('loginname'))        except Users.DoesNotExist:            raise PubErrorCustom("登录账户错误！")        if user.passwd != self.request.data_format.get('passwd'):            raise PubErrorCustom("密码错误！")        # if not request.data_format.get('vercode') or not len(request.data_format.get('vercode')):        #     raise PubErrorCustom("请输入谷歌验证码!")        #        # if not check_google_token(user.google_token,request.data_format.get('vercode')):        #     raise PubErrorCustom("谷歌验证码错误!")        if user.status == 1 :            raise PubErrorCustom("登录账户错误！")        elif user.status == 2 :            raise PubErrorCustom("已冻结！")        userlogin.userid=user.userid        userlogin.ip = request.META.get('REMOTE_ADDR')        userlogin.user_agent =request.META.get('HTTP_USER_AGENT')        userlogin.save()        if user.userid in [170]:            token=Token.objects.filter(userid=user.userid)            if not token.exists():                token = Token.objects.create(userid=user.userid)            else:                token=token[0]                token.key = binascii.hexlify(os.urandom(80)).decode()                token.save()        else:            Token.objects.filter(userid=user.userid).delete()            token = Token.objects.create(userid=user.userid)        header = {"authorization": token.key}        return { "header": header,"msg":"登录成功！"}    @list_route(methods=['POST'])    def qqbot(self, request):        if request.data.get("message_type") == 'group' and request.data.get("message") == 'allwin_qqbot_start':            redis_handler = RedisHandler(db='default', key="allwin_qqbot_start")            res = redis_handler.redis_dict_get()            if res:                res['group_ids'].append(request.data.get("group_id"))                res['group_ids'] = list(set(res['group_ids']))            else:                res = {}                res['group_ids'] = [request.data.get("group_id")]            redis_handler.redis_dict_insert(res)        return HttpResponse("ok")