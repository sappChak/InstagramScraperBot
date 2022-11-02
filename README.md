sudo cp /mnt/c/Users/konot/Desktop/UnFollowers-Checker/session-check_unfollowers_andrew /tmp/.instaloader-andrewcorp
Just put session file to your proeject and then place it to your virtual linux. (command above)
1. source venv/bin/activate
2. flask --app  flask_app run
3. rq worker
4. python3 Execution.py
5.instaloader --login=activity_checker profile profilenamehereobviously --sessionfile=/Desktop/RedisTest/RedisTest/.instaloder-session
6.git rm --cached FILENAME
7.git add FILENAME
8.git commit -m 'Message' 
9.git push

1. virtualvenv venv
2. source venv/bin/activate
3. pip install -r requirements.txt
4. os.getenv('YOUR TELEGRAM BOT TOKEN')
