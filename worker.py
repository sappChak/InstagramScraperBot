import os
from rq import Queue, Worker
import multiprocessing
from redis import Redis


redis_host = os.getenv('REDISHOST')
redis_port = os.getenv('REDISPORT')
redis_client = Redis(host=redis_host, port=redis_port)

queue = Queue(connection=redis_client, default_timeout=-1)


def start_worker(queues, redis_db):
    worker = Worker([queues], connection=redis_db)
    worker.work(max_jobs=500)


if __name__ == '__main__':
    multiprocessing.Process(target=start_worker, args=(queue, redis_client)).start()
