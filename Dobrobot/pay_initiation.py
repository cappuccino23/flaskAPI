import hashlib
import hmac
import json

import psycopg2
import requests
from flask import Flask

app = Flask(__name__)

api_key = 'ds9qKLc8lkl91oM8O71'
secret_key = 'testdobrobot'

conn = psycopg2.connect(dbname='payments_dobrobot', user='dobrobot', password='dobrobot', host='localhost')


def init_pay(in_data):

    merc_pid = add_init_pay(in_data)

    parameters = in_data

    req_data = json.dumps(
        {
            "method": "form",
            "pay_type": "card",
            "params": parameters,
            "merc_data": merc_pid
        })

    sign = hmac.new(bytearray(secret_key, 'utf-8'), bytearray(req_data, 'utf-8'),
                    digestmod=hashlib.sha256).hexdigest()
    headers = {"Content-type": "application/json"}
    url = ' https://demo-api2.inplat.ru/?api_key={0}&sign={1}'.format(api_key, sign)
    r = requests.post(url, data=req_data, headers=headers)
    rec_json = r.json()

    add_to_logs(rec_json)

    return 'Ok'


def add_init_pay(in_data):
    cursor = conn.cursor()

    query = "INSERT INTO public.charity (found, user_id, sum, stamp) VALUES(%s, %s, %s, CURRENT_TIMESTAMP) RETURNING id"

    cursor.execute(query, tuple(in_data.values()))

    merc_id = cursor.fetchone()

    conn.commit()

    return merc_id


def add_to_logs(rec_json):
    cursor = conn.cursor()

    query = "INSERT INTO public.logs(code, message, pay_url,success_callback_url,fail_callback_url, success_redirect_url, fail_redirect_url, init_stamp)" \
            "VALUES(%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP) RETURNING pay_url"

    cursor.execute(query, tuple(rec_json.values()))

    add_url = cursor.fetchone()

    conn.commit()
    conn.close()

    return add_url