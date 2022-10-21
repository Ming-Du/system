import threading


def fun_timer():
    print('Hello Timer!')


timer = threading.Timer(5, fun_timer)
timer.start()
