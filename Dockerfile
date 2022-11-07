FROM python:3.10-slim

COPY . /app
WORKDIR /app

ENV PYTHONUNBUFFERED True

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt

ENV API_TOKEN=5667868424:AAEQFu6U077_lfR3oBVmX6zzvaZkkzLPGds

ENTRYPOINT exec gunicorn -b 0.0.0.0:$PORT --workers 2 --threads 8 --timeout 0 app


EXPOSE $PORT


