import os
from random import randint
import redis

# Init redis client
# 100 USERS or 100 bit-string is quite long, so we generate random binary string
# We can use the api also for testing
# Refer to client.http
r = redis.Redis(host='localhost', port=6379, db=0)
r.flushdb()
binstr = ''.join([str(randint(0, 1)) for n in range(100)])
yesterbin = ''.join([str(randint(0, 1)) for n in range(100)])
os.environ['USER_COUNT'] = str(len(binstr))
date = '25/08/2018'
yester = '24/08/2018'

import redis_module as Fn


def test_count_bit():
    for n in range(len(binstr)):
        r.setbit(date, n, int(binstr[n]))

    expected_setbit = len([n for n in binstr if n == '1'])
    fn_count = Fn.count_user(r, date)
    assert fn_count == expected_setbit

    expected_clearbit = len([n for n in binstr if n == '0'])
    fn_count = Fn.count_absent_user(r, date)
    assert fn_count == expected_clearbit


def test_get_setbit():
    expected = [idx for idx, bit in enumerate(binstr) if bit == '1']
    result = Fn.get_setbits(r, date)
    assert expected == result


def test_get_clearbit():
    expected = [idx for idx, bit in enumerate(binstr) if bit == '0']
    result = Fn.get_setbits(r, date, 0)
    assert expected == result


yesterday = Fn.YESTERDAY(date)


def test_consecutive_present():
    assert yesterday == yester

    for n in range(len(yesterbin)):
        r.setbit(yesterday, n, int(yesterbin[n]))

    idx_today = [idx for idx, bit in enumerate(binstr) if bit == '1']
    idx_yester = [idx for idx, bit in enumerate(yesterbin) if bit == '1']

    common_idx = [n for n in idx_today if n in idx_yester]
    count_common_idx = len(common_idx)
    result_count, result_list = Fn.count_consecutive_present(r, date)

    assert result_list == common_idx
    assert result_count == count_common_idx


def test_consecutive_absent():
    idx_today = [idx for idx, bit in enumerate(binstr) if bit == '0']
    idx_yester = [idx for idx, bit in enumerate(yesterbin) if bit == '0']

    common_idx = [n for n in idx_today if n in idx_yester]
    count_common_idx = len(common_idx)
    result_count, result_list = Fn.count_consecutive_absent(r, date)

    assert result_list == common_idx
    assert result_count == count_common_idx
