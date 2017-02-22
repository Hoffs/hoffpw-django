release: python manage.py migrate
web: gunicorn hoffpw.wsgi --worker-class gevent -b 0.0.0.0:$PORT --log-file -
worker1: celery -A hoffpw worker -B -S django --loglevel=INFO --concurrency=12 -n worker1@hoffpw --without-gossip --without-mingle --without-heartbeat