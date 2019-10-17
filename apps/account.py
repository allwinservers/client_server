
from utils.exceptions import PubErrorCustom
from libs.utils.mytime import UtilTime
from apps.user.models import Users,BalList
from libs.utils.log import logger
from apps.public.utils import get_fee_rule_forSys

class AccountBase(object):

    def __init__(self,**kwargs):

        self.amount = kwargs.get('amount', None)
        if not self.amount:
            raise PubErrorCustom("交易金额不能为空!")
        else:
            self.amount = float(self.amount)

        self.ordercode = kwargs.get('ordercode', 0)

        userid = kwargs.get('userid', None)
        user = kwargs.get('user',None)
        if not (userid or user):
            raise PubErrorCustom("用户代码不能为空!")

        if not user:
            try:
                self.user = Users.objects.select_for_update().get(userid=userid)
            except Users.DoesNotExist:
                raise PubErrorCustom("无对应用户信息({})".format(userid))
        else:
            self.user = user

        logger.info("""动账前: userid:{} upd_bal_date:{} amount:{} ordercode:{} bal:{} cashout_bal:{} stop_bal:{} lastday_bal:{} today_bal:{} lastday_pay_amount:{} 
                        today_pay_amount:{} tot_pay_amount:{} lastday_cashout_amount:{} today_cashout_amount:{} tot_cashout_amount:{}""".format(
            self.user.userid,
            self.user.upd_bal_date,
            self.amount,
            self.ordercode,
            self.user.bal,
            self.user.cashout_bal,
            self.user.stop_bal,
            self.user.lastday_bal,
            self.user.today_bal,
            self.user.lastday_pay_amount,
            self.user.today_pay_amount,
            self.user.tot_pay_amount,
            self.user.lastday_cashout_amount,
            self.user.today_cashout_amount,
            self.user.tot_cashout_amount,
        ))

        self.today = UtilTime().arrow_to_string(format_v="YYYYMMDD")

        self.RunUpdDate()

    def query(self):
        return self.user

    def isUpdDate(self):
        if self.user.upd_bal_date >= self.today:
            return False
        else:
            return True

    def RunUpdDate(self):
        if self.isUpdDate():
            self.user.today_bal = 0.0
            self.user.lastday_bal = self.user.bal

            self.user.today_pay_amount = 0.0
            self.user.lastday_pay_amount = self.user.tot_pay_amount

            self.user.today_cashout_amount = 0.0
            self.user.lastday_cashout_amount = self.user.tot_cashout_amount

            self.user.today_fee_amount = 0.0
            self.user.lastday_fee_amount = self.user.tot_fee_amount

            self.user.upd_bal_date = self.today
            self.user.save()

    def AccountListInsert(self,memo):
        BalList.objects.create(**{
            "userid" : self.user.userid,
            "amount" : self.amount,
            "bal" : self.user.bal,
            "confirm_bal" : float(self.user.bal) + float(self.amount),
            "memo" : memo,
            "ordercode": self.ordercode
        })

    def run(self):
        raise PubErrorCustom("function error!")

class AccountPay(AccountBase):

    """
    动账-充值
    """

    def __init__(self,**kwargs):

        # kwargs.setdefault("isPay",True)
        super().__init__(**kwargs)

    def run(self):
        logger.info("充值")
        self.AccountListInsert("充值")
        self.user.today_pay_amount = float(self.user.today_pay_amount) + self.amount
        self.user.tot_pay_amount = float(self.user.tot_pay_amount) + self.amount

        self.user.today_bal = float(self.user.today_bal) + self.amount
        self.user.bal = float(self.user.bal) + self.amount
        self.user.save()

        logger.info("""动账后: userid:{} upd_bal_date:{} amount:{} ordercode:{} bal:{} cashout_bal:{} stop_bal:{} lastday_bal:{} today_bal:{} lastday_pay_amount:{} 
                        today_pay_amount:{} tot_pay_amount:{} lastday_cashout_amount:{} today_cashout_amount:{} tot_cashout_amount:{}""".format(
            self.user.userid,
            self.user.upd_bal_date,
            self.amount,
            self.ordercode,
            self.user.bal,
            self.user.cashout_bal,
            self.user.stop_bal,
            self.user.lastday_bal,
            self.user.today_bal,
            self.user.lastday_pay_amount,
            self.user.today_pay_amount,
            self.user.tot_pay_amount,
            self.user.lastday_cashout_amount,
            self.user.today_cashout_amount,
            self.user.tot_cashout_amount,
        ))

        return self.user

class AccountCashout(AccountBase):

    """
    动账-提现申请
    """

    def __init__(self, **kwargs):
        kwargs.setdefault("isCashout", True)
        super().__init__(**kwargs)

    def run(self):
        logger.info("提现申请")
        self.user.cashout_bal = float(self.user.cashout_bal) + self.amount
        self.user.save()

        logger.info("""动账后: userid:{} upd_bal_date:{} amount:{} ordercode:{} bal:{} cashout_bal:{} stop_bal:{} lastday_bal:{} today_bal:{} lastday_pay_amount:{} 
                        today_pay_amount:{} tot_pay_amount:{} lastday_cashout_amount:{} today_cashout_amount:{} tot_cashout_amount:{}""".format(
            self.user.userid,
            self.user.upd_bal_date,
            self.amount,
            self.ordercode,
            self.user.bal,
            self.user.cashout_bal,
            self.user.stop_bal,
            self.user.lastday_bal,
            self.user.today_bal,
            self.user.lastday_pay_amount,
            self.user.today_pay_amount,
            self.user.tot_pay_amount,
            self.user.lastday_cashout_amount,
            self.user.today_cashout_amount,
            self.user.tot_cashout_amount,
        ))

        return self.user

class AccountCashoutCanle(AccountBase):

    """
    动账-提现拒绝
    """

    def __init__(self, **kwargs):
        kwargs.setdefault("isCashoutCanle", True)
        super().__init__(**kwargs)

    def run(self):
        logger.info("提现拒绝")
        self.user.cashout_bal = float(self.user.cashout_bal) + self.amount * -1
        self.user.save()

        logger.info("""动账后: userid:{} upd_bal_date:{} amount:{} ordercode:{} bal:{} cashout_bal:{} stop_bal:{} lastday_bal:{} today_bal:{} lastday_pay_amount:{} 
                        today_pay_amount:{} tot_pay_amount:{} lastday_cashout_amount:{} today_cashout_amount:{} tot_cashout_amount:{}""".format(
            self.user.userid,
            self.user.upd_bal_date,
            self.amount,
            self.ordercode,
            self.user.bal,
            self.user.cashout_bal,
            self.user.stop_bal,
            self.user.lastday_bal,
            self.user.today_bal,
            self.user.lastday_pay_amount,
            self.user.today_pay_amount,
            self.user.tot_pay_amount,
            self.user.lastday_cashout_amount,
            self.user.today_cashout_amount,
            self.user.tot_cashout_amount,
        ))
        return self.user

class AccountCashoutConfirm(AccountBase):
    def __init__(self, **kwargs):
        kwargs.setdefault("isCashoutConfirm", True)
        super().__init__(**kwargs)

    def run(self):
        logger.info("提现完成")
        self.amount = self.amount * -1
        self.AccountListInsert("提现")

        self.user.today_cashout_amount = float(self.user.today_cashout_amount) + self.amount * -1
        self.user.tot_cashout_amount = float(self.user.tot_cashout_amount) + self.amount * -1

        self.user.cashout_bal = float(self.user.cashout_bal) + self.amount
        self.user.today_bal = float(self.user.today_bal) + self.amount
        self.user.bal = float(self.user.bal) + self.amount
        self.user.save()
        logger.info("""动账后: userid:{} upd_bal_date:{} amount:{} ordercode:{} bal:{} cashout_bal:{} stop_bal:{} lastday_bal:{} today_bal:{} lastday_pay_amount:{} 
                        today_pay_amount:{} tot_pay_amount:{} lastday_cashout_amount:{} today_cashout_amount:{} tot_cashout_amount:{}""".format(
            self.user.userid,
            self.user.upd_bal_date,
            self.amount,
            self.ordercode,
            self.user.bal,
            self.user.cashout_bal,
            self.user.stop_bal,
            self.user.lastday_bal,
            self.user.today_bal,
            self.user.lastday_pay_amount,
            self.user.today_pay_amount,
            self.user.tot_pay_amount,
            self.user.lastday_cashout_amount,
            self.user.today_cashout_amount,
            self.user.tot_cashout_amount,
        ))

        return self.user

class AccountCashoutConfirmFee(AccountBase):
    def __init__(self, **kwargs):
        kwargs.setdefault("isCashoutConfirm", True)
        kwargs.setdefault("amount",0.1)
        super().__init__(**kwargs)

    def run(self):
        logger.info("手工下发手续费")
        if self.user.fee_rule <= 0.0:
            self.amount = get_fee_rule_forSys()
        else:
            self.amount = float(self.user.fee_rule)
        self.amount = self.amount * -1
        self.AccountListInsert("手工下发手续费")

        self.user.today_fee_amount = float(self.user.today_fee_amount) + self.amount * -1
        self.user.tot_fee_amount = float(self.user.tot_fee_amount) + self.amount * -1

        self.user.today_bal = float(self.user.today_bal) + self.amount
        self.user.bal = float(self.user.bal) + self.amount
        self.user.save()

        logger.info("""动账后: userid:{} upd_bal_date:{} amount:{} ordercode:{} bal:{} cashout_bal:{} stop_bal:{} lastday_bal:{} today_bal:{} lastday_pay_amount:{} 
                        today_pay_amount:{} tot_pay_amount:{} lastday_cashout_amount:{} today_cashout_amount:{} tot_cashout_amount:{}""".format(
            self.user.userid,
            self.user.upd_bal_date,
            self.amount,
            self.ordercode,
            self.user.bal,
            self.user.cashout_bal,
            self.user.stop_bal,
            self.user.lastday_bal,
            self.user.today_bal,
            self.user.lastday_pay_amount,
            self.user.today_pay_amount,
            self.user.tot_pay_amount,
            self.user.lastday_cashout_amount,
            self.user.today_cashout_amount,
            self.user.tot_cashout_amount,
        ))

        return self.user

class AccountStop(AccountBase):

    """
    动账-冻结
    """

    def __init__(self, **kwargs):
        # kwargs.setdefault("isStop", True)
        # kwargs.setdefault("amount", 0.1)
        super().__init__(**kwargs)

    def run(self):
        #3倍冻结,写死
        self.amount *= 3

        logger.info("冻结")
        self.amount = self.amount * -1
        self.AccountListInsert("冻结")

        self.user.stop_bal = float(self.user.stop_bal) + self.amount * -1

        self.user.today_bal = float(self.user.today_bal) + self.amount
        self.user.bal = float(self.user.bal) + self.amount
        self.user.save()
        logger.info("""动账后: userid:{} upd_bal_date:{} amount:{} ordercode:{} bal:{} cashout_bal:{} stop_bal:{} lastday_bal:{} today_bal:{} lastday_pay_amount:{} 
                        today_pay_amount:{} tot_pay_amount:{} lastday_cashout_amount:{} today_cashout_amount:{} tot_cashout_amount:{}""".format(
            self.user.userid,
            self.user.upd_bal_date,
            self.amount,
            self.ordercode,
            self.user.bal,
            self.user.cashout_bal,
            self.user.stop_bal,
            self.user.lastday_bal,
            self.user.today_bal,
            self.user.lastday_pay_amount,
            self.user.today_pay_amount,
            self.user.tot_pay_amount,
            self.user.lastday_cashout_amount,
            self.user.today_cashout_amount,
            self.user.tot_cashout_amount,
        ))

        return self.user

class AccountStopCanle(AccountBase):

    """
    动账-解冻
    """

    def __init__(self, **kwargs):
        kwargs.setdefault("isStopCanle", True)
        super().__init__(**kwargs)

    def run(self):
        #3倍冻结,写死
        self.amount *= 3
        logger.info("解冻")
        self.AccountListInsert("解冻")

        self.user.stop_bal = float(self.user.stop_bal) + self.amount * -1

        self.user.today_bal = float(self.user.today_bal) + self.amount
        self.user.bal = float(self.user.bal) + self.amount
        self.user.save()

        logger.info("""动账后: userid:{} upd_bal_date:{} amount:{} ordercode:{} bal:{} cashout_bal:{} stop_bal:{} lastday_bal:{} today_bal:{} lastday_pay_amount:{} 
                        today_pay_amount:{} tot_pay_amount:{} lastday_cashout_amount:{} today_cashout_amount:{} tot_cashout_amount:{}""".format(
            self.user.userid,
            self.user.upd_bal_date,
            self.amount,
            self.ordercode,
            self.user.bal,
            self.user.cashout_bal,
            self.user.stop_bal,
            self.user.lastday_bal,
            self.user.today_bal,
            self.user.lastday_pay_amount,
            self.user.today_pay_amount,
            self.user.tot_pay_amount,
            self.user.lastday_cashout_amount,
            self.user.today_cashout_amount,
            self.user.tot_cashout_amount,
        ))

        return self.user

class AccountCashoutConfirmForApi(AccountBase):
    def __init__(self, **kwargs):
        kwargs.setdefault("isCashoutConfirm", True)
        super().__init__(**kwargs)

    def run(self):
        logger.info("Api代付")
        self.amount = self.amount * -1
        self.AccountListInsert("Api代付")

        self.user.today_cashout_amount = float(self.user.today_cashout_amount) + self.amount * -1
        self.user.tot_cashout_amount = float(self.user.tot_cashout_amount) + self.amount * -1

        # self.user.cashout_bal = float(self.user.cashout_bal) + self.amount
        self.user.today_bal = float(self.user.today_bal) + self.amount
        self.user.bal = float(self.user.bal) + self.amount
        self.user.save()
        logger.info("""动账后: userid:{} upd_bal_date:{} amount:{} ordercode:{} bal:{} cashout_bal:{} stop_bal:{} lastday_bal:{} today_bal:{} lastday_pay_amount:{} 
                        today_pay_amount:{} tot_pay_amount:{} lastday_cashout_amount:{} today_cashout_amount:{} tot_cashout_amount:{}""".format(
            self.user.userid,
            self.user.upd_bal_date,
            self.amount,
            self.ordercode,
            self.user.bal,
            self.user.cashout_bal,
            self.user.stop_bal,
            self.user.lastday_bal,
            self.user.today_bal,
            self.user.lastday_pay_amount,
            self.user.today_pay_amount,
            self.user.tot_pay_amount,
            self.user.lastday_cashout_amount,
            self.user.today_cashout_amount,
            self.user.tot_cashout_amount,
        ))

        return self.user

class AccountCashoutConfirmForApiFee(AccountBase):
    def __init__(self, **kwargs):
        kwargs.setdefault("isCashoutConfirm", True)
        super().__init__(**kwargs)

    def run(self):
        logger.info("Api代付手续费")
        self.amount = self.amount * -1
        self.AccountListInsert("代付手续费")

        self.user.today_fee_amount = float(self.user.today_fee_amount) + self.amount * -1
        self.user.tot_fee_amount = float(self.user.tot_fee_amount) + self.amount * -1

        self.user.today_bal = float(self.user.today_bal) + self.amount
        self.user.bal = float(self.user.bal) + self.amount
        self.user.save()

        logger.info("""动账后: userid:{} upd_bal_date:{} amount:{} ordercode:{} bal:{} cashout_bal:{} stop_bal:{} lastday_bal:{} today_bal:{} lastday_pay_amount:{} 
                        today_pay_amount:{} tot_pay_amount:{} lastday_cashout_amount:{} today_cashout_amount:{} tot_cashout_amount:{}""".format(
            self.user.userid,
            self.user.upd_bal_date,
            self.amount,
            self.ordercode,
            self.user.bal,
            self.user.cashout_bal,
            self.user.stop_bal,
            self.user.lastday_bal,
            self.user.today_bal,
            self.user.lastday_pay_amount,
            self.user.today_pay_amount,
            self.user.tot_pay_amount,
            self.user.lastday_cashout_amount,
            self.user.today_cashout_amount,
            self.user.tot_cashout_amount,
        ))

        return self.user

class AccountRefreshUpdDate(AccountBase):
    """
    每天凌晨0点0分1秒刷新upd_date时间
    """
    def __init__(self,**kwargs):

        # kwargs.setdefault("isPay",True)
        super().__init__(**kwargs)

    def run(self):
        self.user.save()

        return self.user
