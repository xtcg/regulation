#!/bin/bash

echo "start service ${APP_NAME}"

PID_FILE="/var/run/gunicorn.pid"
echo "Running app $APP_NAME..."
rm -f $PID_FILE
gunicorn -p $PID_FILE