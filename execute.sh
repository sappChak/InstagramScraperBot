export API_TOKEN=5667868424:AAEQFu6U077_lfR3oBVmX6zzvaZkkzLPGds
# shellcheck disable=SC2034
for i in {1..10}
do
  rq worker &
done


