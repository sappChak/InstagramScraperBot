
# shellcheck disable=SC2034
for i in {1..10}
do
  rq worker --url redis://redis:6379 &
done


