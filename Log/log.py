import logging

# Define a log object
log = logging.getLogger('my_logger')
log.setLevel(logging.INFO)

# Create a file handler to write log messages to a file
handler = logging.FileHandler('server.log',encoding='utf-8',mode='w')
handler.setLevel(logging.INFO)

# Create a formatter to customize the log message format
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
handler.setFormatter(formatter)

# Add the handler to the log object
log.addHandler(handler)

log.info('This is an info message, log start')

def switchToStd():
    global log
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')

    # Remove the file handler from the log object
    log.removeHandler(log.handlers[0])

    # Create a handler to write log messages to the standard output stream
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    log.addHandler(handler)

    log.info('This is an info message, log switched to standard output')