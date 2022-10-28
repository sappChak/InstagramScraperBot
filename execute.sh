source venv/bin/activate
gunicorn -w 2 flask_app:app &
# shellcheck disable=SC2034
for i in {1..5}
do
  rq worker &
done


