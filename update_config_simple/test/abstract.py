from abc import ABCMeta
from abc import abstractmethod


class Payclass:

    def pay(self):
        pass


class Ali(Payclass):
    def pay(self, *args, **kwargs):
        print("use ali pay {money}".format(money=args[0]))


class Ten(Payclass):
    def pay(self, *args, **kwargs):
        print("use wei {money}".format(money=args[0]))


class App(Payclass):
    def pay(self, *args, **kwargs):
        print("user apple {money}".format(money=args[0]))


wec = Ali()

app = App()


def pay(obj, *args, **kwargs):
    obj.pay(*args, **kwargs)


pay(wec, "100")
