
for i in {1..100}
do
    python3 worker.py &
done

gunicorn -b 0.0.0.0:8080 --workers 1 --worker-class gevent app