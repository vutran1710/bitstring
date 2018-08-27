import os
import redis
from bitstring import Bits
import random
from datetime import datetime
import redis_module as Fn
from redis_module import USER_COUNT

from flask import Flask
app = Flask(__name__)


REDIS_PORT = 6379
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')

# Init redis client
R = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
R.flushdb()


def GET_DAY():
    return datetime.now().strftime(Fn.DATE_FORMAT)


def MAKE_EMPTY_BITSTRING(day):
    if not R.get(day):
        for n in range(USER_COUNT):
            R.setbit(day, n, 0)
    return R.get(day)


@app.route("/checkin/<user_id>")
def checkin(user_id):
    if int(user_id) >= USER_COUNT:
        return 'User_id out of range'

    today = GET_DAY()
    MAKE_EMPTY_BITSTRING(today)
    current_bit = R.getbit(today, user_id)
    checkedin = R.setbit(today, user_id, 0 if current_bit == 1 else 1)
    return 'User {} has checked {}'.format(user_id, 'in' if not checkedin else 'out')


@app.route("/logged")
def get_today_logged_users():
    day = GET_DAY()
    count = Fn.count_user(R, day)
    user_id_list = Fn.get_setbits(R, day)
    return "total: {} ; users: {}".format(count, user_id_list)


@app.route("/absent")
def get_today_absent_users():
    day = GET_DAY()
    count = Fn.count_absent_user(R, day)
    user_id_list = Fn.get_setbits(R, day, 0)
    return "total: {} ; users: {}".format(count, user_id_list)


@app.route("/workers")
def get_consecutive_present_users():
    day = GET_DAY()
    count, id_list = Fn.count_consecutive_present(R, day)
    return "total: {} ; users: {}".format(count, id_list)


@app.route("/yolos")
def get_consecutive_absent_users():
    day = GET_DAY()
    count, id_list = Fn.count_consecutive_absent(R, day)
    return "total: {} ; users: {}".format(count, id_list)


@app.route("/string")
def get_today_string():
    day = GET_DAY()
    binstr = Bits(bytes=R.get(day) or MAKE_EMPTY_BITSTRING(day)).bin[:USER_COUNT]
    return "Str: {} ;; length: {}".format(binstr, len(binstr))


@app.route("/fake")
def generate_yesterday_data():
    """Here we fake some data for yesterday"""
    day = Fn.YESTERDAY(GET_DAY())

    for n in range(USER_COUNT):
        R.setbit(day, n, random.randint(0, 1))

    binstr = Bits(bytes=R.get(day)).bin[:USER_COUNT]
    logged_count = Fn.count_user(R, day)
    logged_ids = Fn.get_setbits(R, day)
    absent_count = Fn.count_absent_user(R, day)
    absent_ids = Fn.get_setbits(R, day, 0)
    return "Bitstring:({}) {} --\n- Absent: count: {}, ids {}, \n- Logged:count {}, ids {} ".format(
        len(binstr), binstr, absent_count, absent_ids, logged_count, logged_ids)


@app.route("/reset")
def reset_db():
    R.flushdb()
    return "Reset redis"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
