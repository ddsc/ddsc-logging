import logging
import socket

import pika

HOSTNAME = socket.gethostname()


class DDSCHandler(logging.Handler):

    def __init__(self, broker_url):
        super(DDSCHandler, self).__init__()
        self.broker_url = broker_url
        self.is_connected = False

    def connect(self):
        self.connection = pika.BlockingConnection(
            pika.URLParameters(self.broker_url)
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='hello')

    def emit(self, record, depth=1):

        # Note that `self.is_connected == True` does not necessarily mean that
        # we still have a connection: upon entrance of this function, this
        # attribute tells us whether the previous record was logged
        # successfully

        if not self.is_connected:
            try:
                self.connect()
                self.is_connected = True
            except:
                pass

        if self.is_connected and depth < 3:
            try:
                self.channel.basic_publish(
                    exchange='',
                    routing_key='hello',
                    body=self.format(record)
                )
            except:
                # RabbitMQ might be down. Another possibility is that it has
                # been restarted, so it is worthwhile to do a 2nd round.
                self.is_connected = False
                self.emit(record, depth + 1)

    def __del__(self):
        pass
