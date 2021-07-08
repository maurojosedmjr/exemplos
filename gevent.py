from datetime import datetime
import gevent

def fun1():
    print("Fun1", datetime.now())
    gevent.sleep(15)
    print("finalizou a Fun1", datetime.now())


def fun2():
    print("Fun2", datetime.now())
    gevent.sleep(20)
    print("finalizou a Fun2", datetime.now())


def fun3():
    print("Fun3", datetime.now())
    gevent.sleep(5)
    print("finalizou a Fun3", datetime.now())


if __name__ == "__main__":
    start = datetime.now()

    gevent.joinall(
        [
            gevent.spawn(fun1),
            gevent.spawn(fun2),
            gevent.spawn(fun3)
        ]
    )

    end = datetime.now()

    print(end - start)
