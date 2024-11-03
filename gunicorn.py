bind = '127.0.0.1:28000'
workers = 3

backlog = 2048
worker_class = "gevent"
worker_connections = 1000
daemon = False
debug = True
proc_name = 'run'
pidfile = 'log/gunicorn_mock.pid'
accesslog = 'log/gunicorn_access_mock.log'
errorlog = 'log/gunicorn_error_mock.log'
