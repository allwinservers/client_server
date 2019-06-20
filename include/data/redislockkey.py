


#创建订单
BUSINESS_CREATE_OREDER="'BUSINESS_CREATE_OREDER'+'_'+str(request.user.userid)+'_'+str(request.data_format.get('down_ordercode'))"

#自己更改余额
PAY_SELF_UPD_BAL="'PAY_SELF_UPD_BAL'+'_'+str(request.user.userid)"

#管理员修改余额
PAY_ADMIN_UPD_BAL="'PAY_SELF_UPD_BAL'+'_'+str(request.data_format.get('userid'))"

#二维码表
LOAD_QRCODE = "'LOAD_QRCODE'+'_'"


#聚合码回调
sms_call_mobile_CALLBACK="'sms_call_mobile_CALLBACK'+'_'+str(request.data_format.get('name'))+str(request.data_format.get('amout'))"

zhejiangnongxin_call_mobile_CALLBACK="'zhejiangnongxin_call_mobile_CALLBACK'+'_'+str(request.data_format.get('name'))+str(request.data_format.get('amout'))"