from typing import Callable

BY_THREE: Callable = lambda x: x % 3 == 0
BY_FIVE: Callable = lambda x: x % 5 == 0
BY_SEVEN: Callable = lambda x: x % 7 == 0

def run() -> None:

    for i in range(1, 101):
        out: str = ""

        if BY_THREE(i):
            out = "Fizz"
        if BY_FIVE(i):
            out += "Buzz"
        if BY_SEVEN(i):
            out = "Bazz"

        print(out or str(i))



if __name__ == "__main__":
    run()
