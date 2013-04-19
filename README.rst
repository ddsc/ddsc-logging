ddsc-logging
============

In the DDSC project, several applications are collaborating in a distributed environment. To monitor the entire system, it's convenient to aggregate all logging messages in a central place. The ddsc-logging library solves this by providing a handler that sends all disparate messages to a single broker, viz. RabbitMQ. From there on, the messages can be monitored at your console, persisted to a database, etc. Filtering can be done based on 2 criteria: the source (hostname) and severity of the message. The code is large based on the excellent tutorial at `www.rabbitmq.com <http://www.rabbitmq.com/>`_.

Building ddsc-logging
---------------------

Being a library, ddsc-logging is typically used within other applications. To build just ddsc-logging, follow these steps:

First, make sure the Python header files are installed. On Ubuntu::

	sudo apt-get install python-dev

Then, checkout the repository, bootstrap, and run zc.buildout::

	git clone https://github.com/ddsc/ddsc-logging.git
	cd ddsc-logging
	python bootstrap.py
	bin/buildout

Using ddsc-logging
------------------

Register the handler when you configure logging for your application. For example, when `configuring logging from a dictionary <http://docs.python.org/2/library/logging.config.html#logging.config.dictConfig>`_::

	'rmq': {
	    'class': 'ddsc_logging.handlers.DDSCHandler',
	    'level': 'INFO',
	    'broker_url': BROKER_URL,  # E.g. amqp://guest:guest@localhost:5672/%2F
	}

By default, a `topic exchange <http://www.rabbitmq.com/tutorials/tutorial-five-python.html>`_ named ddsc.log is created. This can be overriden by passing another name to the constructor of DDSCHandler.
