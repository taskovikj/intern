from app import celery
from time import sleep



@celery.task()
def make_file(fname, content):
    with open(fname, "w") as f:
        f.write(content)
    return fname, content


@celery.task()
def complex_task(text):
    sleep(15)
    return text