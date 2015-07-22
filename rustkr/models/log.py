
import threading
import time

import settings

class Subscriber(threading.Thread):
    def __init__(self, redis):
        self.pubsub = redis.pubsub()
        self.pubsub.subscribe(settings.CHANNEL + 'out')
        self.result = None
        self.keep_going = True

        threading.Thread.__init__(self)
        
    def run(self):
        while self.keep_going:
            message = self.pubsub.get_message()
            if message and message['type'] != 'subscribe':
                self.result = message['data']
                break
            time.sleep(0.001)
