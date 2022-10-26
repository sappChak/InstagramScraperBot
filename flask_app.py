import ast
import time
from os import path
import redis
from flask import Flask, request
from rq import Queue
from telegram import Bot
import instaloader
import os

bot = Bot(os.getenv('API_TOKEN'))
app = Flask(__name__)
redis = redis.Redis()
queue = Queue(connection=redis, default_timeout=-1)


def welcome(chat_id):
    bot.send_message(chat_id, 'Hi! You have only two attempts to write the username correctly, otherwise you will be '
                              'banned;). Please, type the username carefully. Enter username to start checking out:')


def start_checking_username(chat_id, text):
    bot.send_message(chat_id, f'Wait, I will check correctness.')
    queue.enqueue('flask_app.get_users_followers', args=(chat_id, text))


@app.route('/', methods=["POST"])
def add_task():
    chat_id = request.json["message"]["chat"]["id"]
    username = request.json["message"]["from"]["first_name"]
    print(username)
    if username != 'Andrey' or 'катяша':
        return {'ok': True}
    print(request.json)
    text = request.json["message"]["text"]
    print(text)

    if text == '/start':
        welcome(chat_id)
    else:
        start_checking_username(chat_id, text)

    return {'ok': True}


def get_users_followers(chat_id, requested_username):
    while True:
        try:
            print('Entered')
            profile_loader = instaloader.Instaloader()
            profile_loader.load_session_from_file('check_unfollowers_andrew')
            user_profile = instaloader.Profile.from_username(profile_loader.context, requested_username)
            bot.send_message(chat_id, 'Everything is ok, nickname was correct.')
            time.sleep(5)

            current_followers = []
            for follower in user_profile.get_followers():
                current_followers.append(follower.username)

            if not path.exists(f"followers/follower_list-{requested_username}.txt"):
                with open(file=f'followers/follower_list-{requested_username}.txt', mode='w') as file:
                    file.write(str(current_followers))
            else:
                with open(file=f'followers/follower_list-{requested_username}.txt', mode='r+') as file:
                    old_followers = ast.literal_eval(file.read())

                unfollowers = check_unfollowers(old_followers=old_followers, current_followers=current_followers)
                followers = check_followers(old_followers=old_followers, current_followers=current_followers)

                send_report(chat_id=chat_id, followers=followers, unfollowers=unfollowers)
                with open(file=f'followers/follower_list-{requested_username}.txt', mode='w') as file:
                    file.write(str(current_followers))

        except:
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
        bot.send_message(chat_id, f':{str(followers)[1:-1]} has started subbing you')


def check_unfollowers(old_followers, current_followers):
    return list(set(old_followers) - set(current_followers))


def check_followers(old_followers, current_followers):
    return list(set(current_followers) - set(old_followers))


if __name__ == "__main__":
    app.run()
