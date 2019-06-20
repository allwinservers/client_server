

import datetime
from libs.utils.mytime import send_toTimestamp


def get_today_start_end_timestamp():
    return send_toTimestamp(datetime.datetime.now().strftime('%Y-%m-%d' ) +' 00:00:01'), \
                send_toTimestamp(datetime.datetime.now().strftime('%Y-%m-%d') + ' 23:59:59')


def get_today_start_end_time():
    return datetime.datetime.now().strftime('%Y-%m-%d' ) +' 00:00:01', \
                 datetime.datetime.now().strftime('%Y-%m-%d') + ' 23:59:59'



