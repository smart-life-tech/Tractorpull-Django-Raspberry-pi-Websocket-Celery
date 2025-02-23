#!/bin/bash
#cd /home/pi/Desktop/Tractorpull-Django-Raspberry-pi-Websocket-Celery/
cd /home/pi/Desktop/NEW GUI/New
./redis-stable/src/redis-server &
#redis-server &

sh ./start-django-server.sh &
sh ./start-celery.sh &

chromium-browser http://localhost:8000/competitors/
