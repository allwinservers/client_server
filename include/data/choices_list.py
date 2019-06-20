from apps.pay.utils import QrCodeWechat,QrCodeFlm,QrCodeNxys,QrCodeJyys,QrCodeZjnxfrom apps.public.utils import HelperWechat,HelperFlmchoices={    "qrcode_type": (        ('QR001', '微信个人二维码'),        ('QR005', '付临门聚合支付码'),        ('QR010', '聚合农信易扫'),        ('QR015', '聚合金燕E商'),        ('QR020', '聚合浙江农信'),    ),    "qrtype_link_qrClass":{        ('QR001',QrCodeWechat),        ('QR005',QrCodeFlm),        ('QR010',QrCodeNxys),        ('QR015', QrCodeJyys),        ('QR020', QrCodeZjnx),    },    "helper_link_helperClass": {        ('QR001', HelperWechat),        ('QR005', HelperFlm)    },    "paytype": {        ('0', '支付宝'),        ('1', '微信'),        ('2', '银联'),        ('3', '聚合'),    },    "order_status": {        ('0', '支付成功'),        ('1', '等待支付'),        ('2', '支付失败'),        ('3', '订单过期'),    },    "order_down_status": {        ('0', '支付成功'),        ('1', '等待支付'),        ('2', '回调失败'),        ('3', '订单过期'),    },    "qrcode_status": {        ('0', '启用'),        ('1', '不启用'),        ('2', '失效'),        ('3', '禁用'),        ('4', '删除'),        ('5', '退出助手'),    },    "tranlist_status": {        ('0', '调账'),        ('1', '支付'),        ('2', '提现'),        ('3', '手续费(佣金)')    }}# for k in choices:#     exec("{}={}".format(k,choices.get(k)))def Choices_to_Dict(key):    data={}    if key not in choices:        return data    for item in choices[key]:        data[item[0]] = item[1]    return datadef Choices_to_List(key):    data=[]    if key not in choices:        return data    for item in choices[key]:        data.append({            "key": item[0],            "value": item[1]        })    return dataif __name__ == '__main__':    print(Choices_to_Dict("qrcode_type"))