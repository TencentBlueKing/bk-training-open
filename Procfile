web: gunicorn bluesapps.wsgi -b :$PORT --log-file -
worker: python manage.py celery worker -l info
beat: python manage.py celery beat -l info
