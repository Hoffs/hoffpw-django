release: python manage.py migrate
web: gunicorn hoffpw.wsgi --worker-class gevent -b 0.0.0.0:$PORT --log-file -
worker1: celery -A hoffpw worker --loglevel=INFO -P eventlet -c 500 -n worker1@hoffpw --without-gossip --without-mingle --without-heartbeat
worker2: celery -A proj worker --loglevel=INFO --concurrency=10 -n worker2@hoffpw --without-gossip --without-mingle --without-heartbeat