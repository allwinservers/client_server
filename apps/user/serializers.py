
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from apps.user.models import Users,UserLink,Role,Login
from libs.utils.mytime import timestamp_toTime
from apps.pay.models import PayPass,PayType

from apps.pay.serializers import PayTypeModelSerializer
from apps.order.models import Order

from apps.public.utils import get_sysparam
from libs.utils.mytime import UtilTime

class UsersSerializer1(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'

        validators = [
            UniqueTogetherValidator(
                queryset=Users.objects.all(),
                fields=('loginname',),
                message="登录名重复！"
            ),
        ]

class UsersSerializer(serializers.Serializer):
    userid = serializers.IntegerField()
    name = serializers.CharField()
    loginname = serializers.CharField()

    rolename = serializers.SerializerMethodField()
    rolecode = serializers.IntegerField()
    lastlogintime = serializers.SerializerMethodField()  #上次登录时间

    google_token = serializers.CharField()

    bal = serializers.DecimalField(max_digits=18,decimal_places=2)
    cashout_bal = serializers.DecimalField(max_digits=18,decimal_places=2)
    up_bal = serializers.DecimalField(max_digits=18,decimal_places=2)

    bal4 = serializers.SerializerMethodField()
    bal5 = serializers.SerializerMethodField()
    today_bal = serializers.SerializerMethodField()

    tot_amount = serializers.SerializerMethodField()

    def get_tot_amount(self,obj):
        return round(Users.objects.get(userid=1).bal,2)

    def get_today_bal(self,obj):
        tot = 0
        ut = UtilTime()
        today = ut.arrow_to_string(ut.today, format_v="YYYY-MM-DD")
        today_start = ut.string_to_timestamp(today + ' 00:00:01')
        today_end = ut.string_to_timestamp(today + ' 23:59:59')
        for item in Order.objects.filter( createtime__lte=today_end, createtime__gte=today_start,status="0"):
            tot = float(tot) + float(item.myfee)
        return round(tot,2)

    def get_bal4(self,obj):

        return round(get_sysparam().bal,2)

    def get_bal5(self,obj):

        return round(get_sysparam().business_agent_tot,2)

    def get_rolename(self,obj):
        try:
            return Role.objects.get(rolecode=obj.rolecode).name
        except Role.DoesNotExist:
            return ""

    def get_lastlogintime(self,obj):
        return timestamp_toTime(Login.objects.filter(userid=obj.userid).order_by('-createtime')[0].createtime)



class BallistSerializer(serializers.Serializer):
    userid = serializers.IntegerField()
    name = serializers.CharField()

    ordercode = serializers.IntegerField()
    memo = serializers.SerializerMethodField()

    bal = serializers.DecimalField(max_digits=18, decimal_places=2)
    amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    confirm_bal = serializers.DecimalField(max_digits=18, decimal_places=2)
    createtime = serializers.SerializerMethodField()

    def get_createtime(self,obj):
        return timestamp_toTime(obj.createtime)

    def get_memo(self,obj):
        if obj.memo == '扫码':
            return "支付"
        else:
            return obj.memo

class AgentSerializer(serializers.Serializer):
    userid = serializers.IntegerField()
    name = serializers.CharField()
    loginname = serializers.CharField()
    createtime = serializers.SerializerMethodField()
    concat = serializers.CharField()
    contype = serializers.CharField()

    bal = serializers.DecimalField(max_digits=18, decimal_places=2)
    bal1 = serializers.SerializerMethodField()

    def get_bal1(self,obj):
        return round(float(obj.bal)-float(obj.cashout_bal),2)

    def get_createtime(self,obj):
        return timestamp_toTime(obj.createtime)

class BusinessSerializer(serializers.Serializer):
    userid = serializers.IntegerField()
    name = serializers.CharField()
    loginname = serializers.CharField()
    createtime = serializers.SerializerMethodField()
    concat = serializers.CharField()
    contype = serializers.CharField()
    paypassid = serializers.IntegerField()
    paypassname = serializers.SerializerMethodField()
    up_bal = serializers.DecimalField(max_digits=18, decimal_places=2)
    today_amount = serializers.SerializerMethodField()

    bal = serializers.DecimalField(max_digits=18,decimal_places=2)

    bal1 = serializers.SerializerMethodField()

    agents = serializers.SerializerMethodField()



    paytypes = serializers.SerializerMethodField()

    def get_paytypes(self,obj):
        paytype = PayType.objects.raw("""
            SELECT t1.*,t2.rate,t2.passid,t3.name as paypassname FROM paytype as t1 
            INNER JOIN paypasslinktype as t2 on t1.paytypeid = t2.paytypeid
            INNER JOIN paypass as t3 on t2.passid = t3.paypassid and t3.status='0'
            WHERE 1=1  and t2.to_id=%s  and t2.type=1 order by t1.createtime
        """,[obj.userid])

        return PayTypeModelSerializer(paytype, many=True).data

    def get_today_amount(self,obj):
        tot = 0
        ut = UtilTime()
        today = ut.arrow_to_string(ut.today, format_v="YYYY-MM-DD")
        today_start = ut.string_to_timestamp(today + ' 00:00:01')
        today_end = ut.string_to_timestamp(today + ' 23:59:59')
        for item in Order.objects.filter(userid=obj.userid, createtime__lte=today_end, createtime__gte=today_start,
                                               status="0"):
            tot = float(tot) + float(item.amount)
        return tot

    def get_bal1(self,obj):
        return round(float(obj.bal)-float(obj.cashout_bal),2)

    def get_agents(self,obj):
        return UserLinkModelSerializer(UserLink.objects.filter(userid=obj.userid).order_by("level"),many=True).data

    def get_createtime(self,obj):
        return timestamp_toTime(obj.createtime)

    def get_paypassname(self,obj):
        try:
            pay=PayPass.objects.get(paypassid=obj.paypassid)
            return pay.name
        except PayPass.DoesNotExist:
            return ""

class UserLinkModelSerializer(serializers.ModelSerializer):

    name_to = serializers.SerializerMethodField()

    def get_name_to(self,obj):
        return Users.objects.get(userid=obj.userid_to).name

    class Meta:
        model = UserLink
        fields = '__all__'

        validators = [
            UniqueTogetherValidator(
                queryset=UserLink.objects.all(),
                fields=('userid','userid_to','level',),
                message="登录名重复！"
            ),
        ]


class WaitbnSerializer(serializers.Serializer):
    userid = serializers.IntegerField()
    name = serializers.CharField()
    loginname = serializers.CharField()
    email = serializers.CharField()
    mobile = serializers.CharField()
    createtime = serializers.SerializerMethodField()
    concat = serializers.CharField()
    contype = serializers.CharField()
    agents = serializers.SerializerMethodField()

    def get_createtime(self,obj):
        return timestamp_toTime(obj.createtime)

    def get_agents(self,obj):
        data=[]
        user=Users.objects.raw("""
            SELECT t1.*,t2.level,t2.userid_to,t3.name as name_to FROM user as t1 
              INNER JOIN userlink as t2 on t1.userid=t2.userid
              INNER JOIN user as t3 on t2.userid_to = t3.userid
              WHERE t1.status = '0' and t3.status ='0'
        """)
        for item in user :
            data.append({
                "userid_to" : user.userid_to,
                "name_to" : user.name_to,
                "level" : user.level
            })
        return data


class BankInfoSerializer(serializers.Serializer):
    userid = serializers.IntegerField()
    bank_name = serializers.CharField()
    open_name = serializers.CharField()
    open_bank = serializers.CharField()
    bank_card_number  = serializers.CharField()
