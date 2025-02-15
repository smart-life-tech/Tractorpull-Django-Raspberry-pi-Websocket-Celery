# Tractorpull-Django-Raspberry-pi-Websocket-Celery
django-websocket-celery
======================

Project home: https://github.com/CovidHunter/Tractorpull-Django-Raspberry-pi-Websocket-Celery

### Development

Install system dependencies using a package manager. E.g. for OSX, using homebrew:

    brew install python3
  
Create a virtualenv using Python 3 and install dependencies. I recommend using [virtualenvwrapper](https://virtualenvwrapper.readthedocs.org/en/latest/install.html#basic-installation) to that python. NOTE! You must change 'path/to/python3'
to be the actual path to python3 on your system.

    pip install -r requirements.txt
    or
    pip install --use-deprecated=legacy-resolver -r requirements.txt

  
Run celery:

    celery -A tractor_pull worker -l INFO
  
Run server:

    python manage.py runserver X.X.X.X:[port]
