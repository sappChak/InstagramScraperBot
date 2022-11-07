import ast
import multiprocessing
import time
from os import path
import redis
from flask import Flask, request
from rq import Queue, Worker
from telegram import Bot
import instaloader
import os

#Telegram bot
bot = Bot(os.getenv('API_TOKEN'))

#web app
application = Flask(__name__)

#redis client
redis_host = os.getenv('REDISHOST')
redis_port = os.getenv('REDISPORT')
redis_client = redis.Redis(host=redis_host, port=redis_port)

queue = Queue(connection=redis_client, default_timeout=-1)


def start_worker(queues, redis_db):
    worker = Worker([queues], connection=redis_db)
    worker.work()


def welcome(chat_id):
    bot.send_message(chat_id,
                     f'Hi! Please, type the username carefully. Enter username to start checking out:')


@application.route('/', methods=["POST"])
def add_task():
 
    try:
        chat_id = request.json['message']['chat']['id']
        username = request.json['message']['from']['username']
    except Exception as e:
        return {'ok': True}
    if username != 'scaryfabioamigo' and username != 's_kaate' and username != 'andrejkonotop':  # Currently, bot works privately
        return {'ok': True}

    text = request.json['message']['text']

    if text == '/start':
        welcome(chat_id)
    else:
        queue.enqueue(f=get_users_followers, args=(chat_id, text))
        multiprocessing.Process(target=start_worker, args=(queue, redis_client), daemon=True).start()

    return {'ok': True}


def get_users_followers(chat_id, requested_username):
    profile_loader = instaloader.Instaloader()
    profile_loader.load_session_from_file(username='check_unfollowers_andrew',
                                          filename='session-check_unfollowers_andrew')
    bot.send_message(chat_id, f'I have started staring at {requested_username} ;)')
    while True:
        try:
            bot.send_message(chat_id, 'I am inside the loop')
            user_profile = instaloader.Profile.from_username(profile_loader.context, requested_username)
            time.sleep(5)
            bot.send_message(chat_id, 'I am inside the loop 2')
            current_followers = []
            for follower in user_profile.get_followers():
                current_followers.append(follower.username)

            if not path.exists(f"follower_list-{requested_username}.txt"):
                with open(file=f'follower_list-{requested_username}.txt', mode='w') as file:
                    file.write(str(current_followers))
            else:
                with open(file=f'follower_list-{requested_username}.txt', mode='r+') as file:
                    old_followers = ast.literal_eval(file.read())

                unfollowers = check_unfollowers(old_followers=old_followers, current_followers=current_followers)
                followers = check_followers(old_followers=old_followers, current_followers=current_followers)

                send_report(chat_id=chat_id, followers=followers, unfollowers=unfollowers)
                with open(file=f'follower_list-{requested_username}.txt', mode='w') as file:
                    file.write(str(current_followers))

            bot.send_message(chat_id, f'I am here, but new files were not created. {os.listdir()}')

        except Exception as e:
            print(e)
            bot.send_message(chat_id, f'Profile {requested_username} does not exist')
            break
        time.sleep(900)


def send_report(chat_id, followers, unfollowers):
    if followers == [] and unfollowers == []:
        print("No change in followers, so not sending message to telegram")
        return

    if not followers:
        followers = 'None'

    if not unfollowers:
        unfollowers = 'None'

    if unfollowers != 'None':
        bot.send_message(chat_id, f"I've caught unfollower's username:{str(unfollowers)[1:-1]}")

    if followers != 'None':
        bot.send_message(chat_id, f':{str(followers)[1:-1]} has/have started subbing you')


def check_unfollowers(old_followers, current_followers):
    return list(set(old_followers) - set(current_followers))


def check_followers(old_followers, current_followers):
    return list(set(current_followers) - set(old_followers))


if __name__ == "__main__":
     application.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
