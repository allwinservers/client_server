


from rest_framework import serializers
from apps.user.models import Users,Login
from django.utils import timezone
from rest_framework.validators import UniqueTogetherValidator

from apps.public.models import Qrcode,WechatHelper
from apps.paycall.models import PayCallList

from libs.utils.mytime import timestamp_toTime,UtilTime


class WechatHelperModelSerializer(serializers.ModelSerializer):
	status_name = serializers.SerializerMethodField()


	def get_status_name(self,obj):
		return "登录" if str(obj.login) == '0' else "未登录"

	class Meta:
		model = WechatHelper
		fields = '__all__'

		validators = [
			UniqueTogetherValidator(
				queryset=WechatHelper.objects.all(),
				fields=('name',),
				message="店员名称不能重复！"
			),
		]


class QrcodeModelSerializer(serializers.ModelSerializer):

	statusname = serializers.SerializerMethodField()

	createtime = serializers.SerializerMethodField()

	tot = serializers.SerializerMethodField()
	today = serializers.SerializerMethodField()


	def get_tot(self,obj):
		tot = 0
		for item in PayCallList.objects.filter(name=obj.name,status="0"):
			tot = float(tot) + float(item.amount)
		return tot

	def get_today(self,obj):
		tot = 0
		ut = UtilTime()
		today = ut.arrow_to_string(ut.today,format_v="YYYY-MM-DD")
		today_start = ut.string_to_timestamp(today + ' 00:00:01')
		today_end = ut.string_to_timestamp(today + ' 23:59:59')
		for item in PayCallList.objects.filter(name=obj.name,createtime__lte=today_end,createtime__gte=today_start,status="0"):
			tot = float(tot) + float(item.amount)
		return tot

	def get_statusname(self,obj):

		if str(obj.status) == '0':
			return '启用'
		elif  str(obj.status) == '1':
			return '不启用'
		elif  str(obj.status) == '2':
			return '失效'
		elif str(obj.status) == '3':
			return '禁用'

	def get_createtime(self,obj):
		return timestamp_toTime(obj.createtime)

	class Meta:
		model = Qrcode
		fields = '__all__'


class ManageSerializer(serializers.Serializer):

	userid = serializers.IntegerField()
	loginname = serializers.CharField()
	name  = serializers.CharField()
	rolename = serializers.CharField()

	logintime = serializers.SerializerMethodField()
	logincount = serializers.SerializerMethodField()
	ip = serializers.SerializerMethodField()

	def get_logintime(self,obj):
		login=Login.objects.filter(userid=obj.userid).order_by("createtime")
		return timestamp_toTime(login[0].createtime) if login.exists() else ""

	def get_logincount(self,obj):
		return Login.objects.filter(userid=obj.userid).count()

	def get_ip(self,obj):
		login=Login.objects.filter(userid=obj.userid).order_by("createtime")
		return login[0].ip if login.exists() else ""


