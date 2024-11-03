import gevent.monkey
gevent.monkey.patch_all()

import os
import multiprocessing

# debug = True
loglevel = 'debug'
bind = "0.0.0.0:16000"
pidfile = "log/gunicorn_kg.pid"
accesslog = "log/gunicorn_access_kg.log"
errorlog = "log/gunicorn_debug_kg.log"
daemon = True

# 启动的进程数
# workers = multiprocessing.cpu_count()//4
workers = 3

worker_class = 'gevent'
x_forwarded_for_header = 'X-FORWARDED-FOR'
