from django.db import models

class OrderCount(models.Model):

    id = models.BigAutoField(primary_key=True)

    userid = models.BigIntegerField(verbose_name="用户ID", default=0)

    today_amount = models.DecimalField(max_digits=18,decimal_places=6,default=0.000,verbose_name="当天流水")
    today_rate = models.DecimalField(max_digits=18, decimal_places=6, default=0.000, verbose_name="当天成功率")

    tot_order_count = models.IntegerField(verbose_name="当天总订单数")
    today_success_order_count = models.IntegerField(verbose_name="当天成功订单数")
    today = models.CharField(max_length=10)

    class Meta:
        verbose_name = '订单统计'
        verbose_name_plural = verbose_name
        db_table = 'ordercount'