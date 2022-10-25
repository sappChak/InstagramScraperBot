source venv/bin/activate
flask --app  flask_app run
# shellcheck disable=SC2034
for i in {1..10}
do
  rq worker &
done


