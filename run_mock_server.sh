#!/usr/bin/env bash
echo 'Stop services...'
ps -ux | grep run_mock_server:app | awk '{print $2}' | xargs kill -9
echo 'Restart services...'
#nohup gunicorn -c gunicorn.py  run_mock_server:app -b 0.0.0.0:18000 -t 600000 --timeout 600000 -k gevent >> log/mock_server.log 2>&1 &
gunicorn -c gunicorn.py run_mock_server:app -b 0.0.0.0:18000 -t 600000 --timeout 600000 -k gevent 
echo 'Done'
