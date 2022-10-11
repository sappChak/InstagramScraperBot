import ast
import time
from os import path
import redis
from flask import Flask, request
from rq import Queue
from telegram import Bot
import instaloader

import config

bot = Bot(config.API_TOKEN)
app = Flask(__name__)
redis = redis.Redis()
queue = Queue(connection=redis, default_timeout=99999999)


def welcome(chat_id):
    bot.send_message(chat_id, 'Мяууууу')


@app.route('/', methods=["POST"])
def add_task():
    chat_id = request.json["message"]["chat"]["id"]
    print(request.json)
    text = request.json["message"]["text"]
    print(text)
    if text == '/start':
        welcome(chat_id)
    else:

        bot.send_message(chat_id, f'Чекайно, зараз подивлюсь чи не наїбав(ла) ти мене...')
        # if wrong_username():
        #     bot.send_message(chat_id, 'Давай по новой, всё хуйня')
        #     return {'ok': True}
        bot.send_message(chat_id,
                         f'Все добре, написав(ла) нік правильно(слава Аллаху). РОЗПОЧАТО слідкування за {text}')

        queue.enqueue('flask_app.get_users_followers', chat_id)

    return {'ok': True}

def get_users_followers(chat_id):
    while True:
        try:
            print('Entered')
            profile_loader = instaloader.Instaloader()
            profile_loader.load_session_from_file('activity_checker', filename='/mnt/c/Users/konot/Desktop/mytutorial/RedisTest/session-activity_checker')
            profile_loader.login(config.USERNAME, config.PASSWORD)
            user_profile = instaloader.Profile.from_username(profile_loader.context, "scaryfabioamigo")
            print('Entered')
            time.sleep(2)

            current_followers = []
            for follower in user_profile.get_followers():
                current_followers.append(follower.username)

            if not path.exists("follower_list.txt"):
                with open(file='follower_list.txt', mode='w') as file:
                    file.write(str(current_followers))
            else:
                with open(file='follower_list.txt', mode='r+') as file:
                    old_followers = ast.literal_eval(file.read())

                unfollowers = check_unfollowers(old_followers=old_followers, current_followers=current_followers)
                followers = check_followers(old_followers=old_followers, current_followers=current_followers)

                send_report(chat_id=chat_id, followers=followers, unfollowers=unfollowers)
                with open(file='follower_list.txt', mode='w') as file:
                    file.write(str(current_followers))

        except Exception as e:
            print(e)
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
        bot.send_message(chat_id, f"ACHTUNG!!! Погоняло покидька, який від Вас відписався:{str(unfollowers)[1:-1]}")

    if followers != 'None':
        bot.send_message(chat_id, f'Алло, там нік красавчика, який зважився Вас сабати:{str(followers)[1:-1]}')


def check_unfollowers(old_followers, current_followers):
    return list(set(old_followers) - set(current_followers))


def check_followers(old_followers, current_followers):
    return list(set(current_followers) - set(old_followers))


if __name__ == "__main__":
    app.run()
