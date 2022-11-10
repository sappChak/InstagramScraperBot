import ast
import time
from os import path
from flask import Flask, request
from telegram import Bot
import instaloader
import os
import random

# Telegram bot
bot = Bot(os.getenv('API_TOKEN'))

# web app
application = Flask(__name__)


def welcome(chat_id):
    bot.send_message(chat_id,
                     f'Andrew on the bit. Ник свой напиши, не дай Бог неправильно - забаню нахуй :)')


@application.route('/', methods=["POST"])
def add_task():
    # from worker import redis_client
    # redis_client.flushdb()
    # redis_client.flushall()
    # return {'ok': True}
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
        from worker import queue
        # queue.enqueue(f=get_users_followers, args=(chat_id, text), job_timeout=-1)
        # queue.create_job(func='app.get_users_followers', args=(chat_id, text))
        queue.enqueue_call(func=get_users_followers, args=(chat_id, text), timeout=-1)

    return {'ok': True}


def get_users_followers(chat_id, requested_username):
    profile_loader = instaloader.Instaloader()
    profile_loader.load_session_from_file(username='instaunfollow2022', filename='session-instaunfollow2022')

    bot.send_message(chat_id, f'Расслабься, самое сложно позади')
    while True:
        try:
            # bot.send_message(chat_id, 'I am inside the loop')
            user_profile = instaloader.Profile.from_username(profile_loader.context, requested_username)
            # bot.send_message(chat_id, 'I am inside the loop 2')
            current_followers = []
            for follower in user_profile.get_followers():
                current_followers.append(follower.username)
            time.sleep(5)
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

            # bot.send_message(chat_id, f'I am here, but new files were not created. {os.listdir()}')
            print(f'{os.listdir()}')

        except Exception as e:
            print(e)
            bot.send_message(chat_id, f'Напрягайся, такого ника: {requested_username} не существует. Я предупреждал.')
            break
        time.sleep(random.uniform(2500, 2800))


def send_report(chat_id, followers, unfollowers):
    if followers == [] and unfollowers == []:
        print("No change in followers, so not sending message to telegram")
        return

    if not followers:
        followers = 'None'

    if not unfollowers:
        unfollowers = 'None'

    if unfollowers != 'None':
        bot.send_message(chat_id, f"Ник чмони :{str(unfollowers)[1:-1]}")

    if followers != 'None':
        bot.send_message(chat_id, f':{str(followers)[1:-1]} вкрашился в тебя')


def check_unfollowers(old_followers, current_followers):
    return list(set(old_followers) - set(current_followers))


def check_followers(old_followers, current_followers):
    return list(set(current_followers) - set(old_followers))


# if __name__ == "__main__":
#     application.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
