#!/bin/bash

cd Tractorpull-Django-Raspberry-pi-Websocket-Celery/

./redis-stable/src/redis-server &

sh ./start-django-server.sh &
sh ./start-celery.sh &

chromium-browser http://localhost:8000/competitors/
