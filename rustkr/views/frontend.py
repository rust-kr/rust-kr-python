# -*- encoding:utf-8 -*-
import random
import time
import json
import redis
import flask
from flask import Module

from ..models.log import Subscriber

import settings

frontend = Module(__name__)

client = redis.Redis(db=7)

def parse_data(data):
    strtime, nick, message = data.split(':', 2)
    return float(strtime), nick, message.decode('utf-8')


@frontend.route('/')
def index():
    logs = client.lrange(settings.CHANNEL, 0, 9)
    data = []
    for log in reversed(logs):
        datum = parse_data(log)
        data.append(datum)
    lasttime = data[-1][0]
    nick = 'web%04d' % random.choice(range(0,1000))
    return flask.render_template('index.html', logs=data, randnick=nick, lasttime=lasttime)

@frontend.route('/api/update', methods=['POST'])
def update():
    try:
        strtime = flask.request.values['time']
    except:
        strtime = '0'
    reqtime = int(strtime)
    lines = client.lrange(settings.CHANNEL, 0, 9)
    new = []
    for line in reversed(lines):
        data = parse_data(line)
        if data[0] <= reqtime: continue
        new.append(data)
    
    if len(new) == 0:
        subscriber = Subscriber(client)
        subscriber.start()
        for x in xrange(0, 300):
            time.sleep(1)
            if subscriber.result is not None:
                print subscriber.result
                new.append(parse_data(subscriber.result))
                break

    return json.dumps(new)

@frontend.route('/api/send', methods=['POST'])
def send():
    nick = flask.request.values['nick']
    text = flask.request.values['text']
    redismsg = ':'.join((str(int(time.time())), nick, text))
    client.lpush(settings.CHANNEL, redismsg)
    client.publish(settings.CHANNEL + 'in', redismsg)
    client.publish(settings.CHANNEL + 'out', redismsg)
    return ''
