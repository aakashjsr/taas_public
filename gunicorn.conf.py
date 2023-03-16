# gunicorn.conf.py
# Non logging stuff
bind = "0.0.0.0:8080"
workers = 3
# Access log - records incoming HTTP requests
accesslog = "./logs/gunicorn.access.log"
# Error log - records Gunicorn server goings-on
errorlog = "./logs/gunicorn.error.log"
# Whether to send Django output to the error log
capture_output = False
# How verbose the Gunicorn error logs should be
loglevel = "debug"

timeout = 600
