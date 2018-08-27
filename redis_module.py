import os
from datetime import datetime, timedelta

# If user number is not multiple of 8, we determine a padding
USER_COUNT = int(os.environ.get('USER_COUNT', 100))
DATE_FORMAT = '%d/%m/%Y'


def ABSENT_KEY(r, day):
    # Update absence_key, and return key
    absence_key = 'abs:{}'.format(day)
    r.bitop('NOT', absence_key, day)
    return absence_key


def YESTERDAY(day):
    delta = timedelta(days=-1)
    day = datetime.strptime(day, DATE_FORMAT)
    return (day + delta).strftime(DATE_FORMAT)


def count_user(r, day):
    return r.bitcount(day)


def count_absent_user(r, day):
    return USER_COUNT - r.bitcount(day)


def get_setbits(r, key, bit=1):
    list = [n for n in range(USER_COUNT) if r.getbit(key, n) == bit]
    return list


def count_consecutive_present(r, today):
    yesterday = YESTERDAY(today)
    consecutive_day_key = '{}-{}'.format(yesterday, today)
    r.bitop('AND', consecutive_day_key, today, yesterday)
    count = r.bitcount(consecutive_day_key)
    consecutive_presents = get_setbits(r, consecutive_day_key)
    return count, consecutive_presents


def count_consecutive_absent(r, day):
    yesterday = YESTERDAY(day)
    consecutive_day_key = '{}-{}'.format(yesterday, day)
    r.bitop('OR', consecutive_day_key, day, yesterday)
    count = USER_COUNT - r.bitcount(consecutive_day_key)
    consecutive_absent = get_setbits(r, consecutive_day_key, 0)
    return count, consecutive_absent
