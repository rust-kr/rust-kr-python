
import threading

import settings

class Subscriber(threading.Thread):
    def __init__(self, redis):
        self.pubsub = redis.pubsub()
        self.pubsub.subscribe(settings.CHANNEL + 'out')
        self.result = None

        threading.Thread.__init__(self)
        
    def run(self):
        self.listener = self.pubsub.listen()
        while True:
            message = self.listener.next()
            if message['type'] == 'subscribe':
                continue
            self.result = message['data']
            break
