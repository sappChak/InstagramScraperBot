FROM python:3.10-slim

COPY . /app
WORKDIR /app

ENV PYTHONUNBUFFERED True

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt

ENV API_TOKEN=5667868424:AAEQFu6U077_lfR3oBVmX6zzvaZkkzLPGds

EXPOSE $PORT

CMD exec gunicorn -b 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 app

RUN ./execute.sh

