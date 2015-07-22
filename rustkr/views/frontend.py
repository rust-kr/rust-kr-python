# -*- encoding:utf-8 -*-
import random
import time
import json
import redis
import flask
from functools import wraps
from flask import Module, request, current_app

from ..models.log import Subscriber

import settings

frontend = Module(__name__)

client = redis.Redis(db=7)

def parse_data(data):
    strtime, nick, message = data.split(':', 2)
    return float(strtime), nick.decode('utf-8'), message.decode('utf-8')

def jsonp(func): # http://flask.pocoo.org/snippets/79/
    """Wraps JSONified output for JSONP requests."""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback and all(c=='_' or 'a'<=c<='z' or '0'<=c<='9' for c in callback.lower()) and not callback[0].isdigit():
            data = str(func(*args, **kwargs))
            content = str(callback) + '(' + data + ')'
            mimetype = 'application/javascript'
            return current_app.response_class(content, mimetype=mimetype)
        else:
            return func(*args, **kwargs)
    return decorated_function


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

@frontend.route('/api/update', methods=['GET', 'POST'])
@jsonp
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
        subscriber.join(10)
        subscriber.keep_going = False # weed the thread out
        if subscriber.result is not None:
            print subscriber.result
            new.append(parse_data(subscriber.result))

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
