


from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from libs.utils.mytime import UtilTime
from apps.weibohongbao.models import WeiboUser,WeiboGroup,WeiboGroupMember,WeiboTask,WeiboSendList

class WeiboUserModelSerializer(serializers.ModelSerializer):

    createtime_format = serializers.SerializerMethodField()
    logintime_format = serializers.SerializerMethodField()
    status_format = serializers.SerializerMethodField()
    type_format = serializers.SerializerMethodField()
    session_status_format = serializers.SerializerMethodField()

    def get_createtime_format(self,obj):
        return UtilTime().timestamp_to_string(obj.createtime)

    def get_logintime_format(self,obj):
        return UtilTime().timestamp_to_string(obj.logintime)

    def get_session_status_format(self,obj):
        return "存活" if obj.session_status=='0' else '失效'

    def get_status_format(self,obj):
        return "是" if obj.status=='0' else '否'

    def get_type_format(self,obj):
        return "发红包" if obj.type=='0' else '抢红包'

    class Meta:
        model = WeiboUser
        fields = '__all__'


class WeiboGroupModelSerializer(serializers.ModelSerializer):

    createtime_format = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()

    def get_createtime_format(self,obj):
        return UtilTime().timestamp_to_string(obj.createtime)

    def get_count(self,obj):
        return WeiboGroupMember.objects.filter(group_id=obj.group_id).count()

    class Meta:
        model = WeiboGroup
        fields = '__all__'

class WeiboTaskModelSerializer(serializers.ModelSerializer):


    date_format = serializers.SerializerMethodField()
    progree_format = serializers.SerializerMethodField()
    umark_format = serializers.SerializerMethodField()
    minamount = serializers.DecimalField(max_digits=18,decimal_places=0)
    maxamount = serializers.DecimalField(max_digits=18,decimal_places=0)
    amountTot = serializers.SerializerMethodField()

    def get_amountTot(self,obj):
        return "%.2lf"%(obj.amountwhat * obj.robnumber)

    def get_umark_format(self,obj):
        return '已开启' if obj.umark=='0' else '未开启'
    def get_date_format(self,obj):
        return obj.date.replace('-','/')

    def get_progree_format(self,obj):
        rate = "0%"
        wbSLObj = WeiboSendList.objects.filter(taskid=obj.taskid)
        if wbSLObj.exists():
            amount = 0.0
            for item in wbSLObj:
                price = float(item.amount) / item.sendcount
                amount += price * float(item.getcount)
            rate = "%.2lf"%(amount * 100.0 / (float(obj.amountwhat) * float(obj.robnumber)))+'%'
        return  rate
    class Meta:
        model = WeiboTask
        fields = '__all__'


class WeiboGroupMemberModelSerializer(serializers.ModelSerializer):

    createtime_format = serializers.SerializerMethodField()

    def get_createtime_format(self,obj):
        return UtilTime().timestamp_to_string(obj.createtime)

    class Meta:
        model = WeiboGroupMember
        fields = '__all__'

class WeiboSendListModelSerializer(serializers.ModelSerializer):

    createtime_format = serializers.SerializerMethodField()
    status_format = serializers.SerializerMethodField()
    amount = serializers.DecimalField(max_digits=18, decimal_places=2)

    def get_status_format(self,obj):
        return "已抢完" if obj.status=='0' else '正在抢'

    def get_createtime_format(self,obj):
        return UtilTime().timestamp_to_string(obj.createtime)

    class Meta:
        model = WeiboSendList
        fields = '__all__'
