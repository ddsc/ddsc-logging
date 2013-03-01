import json
import logging
import socket

import pika


class DDSCHandler(logging.Handler):
    """A handler for distributed event logging.

    Log records are published to a topic exchange named `ddsc.log`. Routing
    criteria will be the hostname of the server and severity of the log
    record. Based on the excellent tutorial at the RabbitMQ website:
    http://www.rabbitmq.com/tutorials/tutorial-five-python.html

    """

    def __init__(self, broker_url, exchange="ddsc.log"):
        """Initialize a new DDSC logging handler.

        Note that `broker_url` should be URL encoded. When using the default
        exchange, for example, the final forard slash must be represented
        as `%2F`.

        """
        super(DDSCHandler, self).__init__()
        self.broker_url = broker_url
        self.exchange = exchange
        self.is_connected = False

    def __connect(self):

        # Setting up a connection is expensive, so we want to reuse it once it
        # is created. Measures are taken to automatically reconnect when a
        # connection is lost. If this fails, a record is considered lost.

        # Both connection and channel have an `is_connected` attribute. This,
        # however, always returns `True`, even if you shut down RabbitMQ.
        # For that reason, a custom `is_connected` flag is used.
        # See: https://github.com/pika/pika/issues/104

        # TODO: investigate asynchronous publishing.

        self.connection = pika.BlockingConnection(
            pika.URLParameters(self.broker_url)
        )

        # Creating a channel is supposed to be cheap. Should a channel be set
        # up and torn down for each logging event, or is it more appropriate
        # to reuse a channel as well? Let's try the latter until it is
        # proven to be wrong.

        self.channel = self.connection.channel()
        self.channel.exchange_declare(
            exchange=self.exchange,
            type='topic',
            durable=True
        )

    def emit(self, record, depth=1):
        """Log the specified logging record.

        Keyword arguments:
        record -- record to log
        depth -- condition to end recursion (don't pass yourself)

        """

        # Note that `self.is_connected == True` does not necessarily mean that
        # we still have a connection: upon entrance of this function, this
        # attribute tells us whether the previous record was logged
        # successfully. See my comments on `is_connected` above.

        if not self.is_connected:

            try:
                self.__connect()
                self.is_connected = True
            except:
                pass

        if self.is_connected and depth < 3:

            try:

                # The message attribute is only available on record
                # if Formatter.format() was invoked earlier.

                if not hasattr(record, 'message'):
                    self.format(record)

                # Publish the message along with useful metadata. Do not send
                # the fully formatted message, i.e. self.format(record), as
                # formatting can be different on each individual server;
                # rather send a dictionary of useful pieces instead.
                #
                # The `asctime` is sent for convenience, e.g. when inspecting
                # messages directly via the RabbitMQ management interface.
                # For further processing, however, `time` is more useful,
                # because `asctime` is not reliably formatted as
                # `2003-07-08 16:49:45,896`. See:
                # http://docs.python.org/3.2/library/logging.html#
                # logrecord-attributes
                #
                # TODO: if no formatter has been set on the logger,
                # the `asctime` attribute is not available,
                # resulting in an exception!

                body = json.dumps({
                    'source': record.pathname,  # full pathname of source file
                    'host': socket.gethostname(),  # hostname
                    'level': record.levelname,  # severity (DEBUG, INFO, etc)
                    'line': record.lineno,  # source line number
                    'message': record.message,  # the log message
                    'time': record.created,  # seconds since epoch
#                   'asctime': record.asctime,  # human-readable time
                })

                # Allow for filtering based on hostname and severity.

                routing_key = "{0}.{1}".format(
                    socket.gethostname(),
                    record.levelname
                )

                # Publish the message.

                self.channel.basic_publish(
                    body=body,
                    exchange=self.exchange,
                    routing_key=routing_key,
                )

            except:

                # RabbitMQ might be down. Another possibility is that it has
                # been restarted, so it is worthwhile to do a 2nd round.

                self.is_connected = False
                self.emit(record, depth + 1)
