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
redis = redis.Redis()
queue = Queue(connection=redis, default_timeout=999999)
app = Flask(__name__)


def welcome(chat_id):
    bot.send_message(chat_id, 'Мяууууу')


@app.route('/', methods=["POST"])
def add_task():
    chat_id = request.json["message"]["chat"]["id"]
#    username = request.json["message"]["from"]["username"]
#    if username != 'scaryfabioamigo':
#        return {'ok': True}
    print(request.json)
    text = request.json["message"]["text"]
    print(text)

    if text == '/start':
        welcome(chat_id)
    else:
        return {'ok': True}
        bot.send_message(chat_id, f'Чекайно, зараз подивлюсь чи не наїбав(ла) ти мене...')
        # if wrong_username():
        #     bot.send_message(chat_id, 'Давай по новой, всё хуйня')
        #     return {'ok': True}
        bot.send_message(chat_id,
                         f'Все добре, написав(ла) нік правильно(слава Аллаху). РОЗПОЧАТО слідкування за {text}')
        from rq import Connection, Worker

        with Connection():
            worker = Worker(queue)
            worker.work()

        queue.enqueue('flask_app.get_users_followers', args=(chat_id, text))

    return {'ok': True}


def get_users_followers(chat_id, requested_username):
    while True:
        try:

            print('Entered')
            profile_loader = instaloader.Instaloader()
            profile_loader.load_session_from_file('activity_checker')
            user_profile = instaloader.Profile.from_username(profile_loader.context, requested_username)
            print('Entered')
            time.sleep(5)

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
