web: flask run --port $PORT --host 0.0.0.0
web: gunicorn app:app --log-file=-
web: gunicorn — worker-class eventlet -w 1 app:app