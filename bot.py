
# -*- coding: utf-8 -*-
import time
import threading
import redis

from easyirc.client.bot import BotClient
from easyirc.const import *
from easyirc import util, settings

import settings as bot_settings

connopt = settings.connections.values()[0]

redisc = redis.Redis(db=7)
pubsub = redisc.pubsub()
for chan in connopt.autojoins:
    pubsub.subscribe(chan + 'in')
listener = pubsub.listen()

class Listener(threading.Thread):
    def run(self):
        for item in listener:
            if item['type'] == 'subscribe': continue
            if item['type'] == 'message':
                chan = item['channel'][:-2]
                strtime, sender, message = item['data'].split(':', 2)
                ircmsg = '<{sender}> {message}'.format(sender=sender, message=message)
                client.privmsg(chan, ircmsg.decode('utf-8'))

bglistener = Listener()
bglistener.daemon = True
bglistener.start()

client = BotClient()

def mask(nick):
    for white in bot_settings.NICK_WHITELIST:
        if nick.startswith(white):
            return nick.encode('utf-8')
    return '*' * len(nick)

@client.events.hookmsg(PRIVMSG)
def on_message(connection, sender, target, message):
    if target[0] != '#': return
    identity = util.parseid(sender)
    masked = mask(identity.nick)
    redismsg = ':'.join((str(int(time.time())), masked, message.encode('utf-8')))
    starget = target.decode('utf-8')
    redisc.lpush(starget, redismsg)
    redisc.publish(starget + 'out', redismsg)

starttime = str(int(time.time()))
redisc.lpush(settings.CHANNEL, starttime + ':rust-kr.org:** 연결이 재시작되었습니다 **')
client.start()

client.interactive()
client.quit(u'Keyboard Interuppt')
