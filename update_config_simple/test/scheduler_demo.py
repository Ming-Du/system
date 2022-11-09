import schedule
import time


def job(name_1):
    print("her name is:{0}".format(name_1))


name = "longsongpong"
schedule.every(1).seconds.do(job, name)

while True:
    schedule.run_pending()
    time.sleep(1)
