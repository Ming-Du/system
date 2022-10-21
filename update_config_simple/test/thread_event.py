import threading
import time

event = threading.Event


def driver(name):
    i = 0
    while True:
        i = i + 1
        print("name" + "driving,drive" + str(i * 60) + "Km")
        time.sleep(1)
        event.wait()
        print(name + "cross light red")


def sign():
    print("light green initial")
    event.set()
    while True:
        time.sleep(3)
        if event.is_set():
            print("light red ,all vihicle cannot cross")
            event.clear()
        else:
            print("light green , all vihicle can cross")
            event.set()


if __name__ == "__main__":
    highwayThreads = []
    bmwCar = threading.Thread(target=driver, args=("BMWCAR",))
    vwCar = threading.Thread(target=driver, args=("VMCAR",))
    highwayThreads.append(bmwCar)
    highwayThreads.append(vwCar)
    for thread in highwayThreads:
        thread.start()
    sign()
