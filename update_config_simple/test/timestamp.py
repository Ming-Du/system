#!/usr/bin/env python
import os
from time import sleep
import signal
import time

child_pid = 0


def signal_handler(signum, frame):
    print("recv signal:{0}".format(signum))
    pid, exit_status = os.waitpid(0, os.WNOHANG)
    print("sub pid:{0},status:{1}".format(pid, exit_status))


def main():
    signal.signal(signal.SIGCHLD, signal_handler)
    pid = os.fork()
    while True:
        if pid < 0:
            print("error create process")
            break
        if pid > 0:
            global child_pid
            child_pid = pid
            print("parent process:pid:{0}".format(os.getpid()))
            break
        if pid == 0:
            print("sub process,pid:{0}".format(os.getpid()))
            sleep(10)
            exit(0)
            break
        break

    while True:
        print("father process:{0} doing...".format(os.getpid()))
        sleep(1)


if __name__ == "__main__":
    main()
