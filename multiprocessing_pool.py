from multiprocessing.pool import ThreadPool
from time import sleep
from datetime import datetime
from typing import List

RRANGE: range = range(10, 0, -1)
MAX_POOL: int = 4


def wait(seconds: int = 5) -> str:
    print(f"Waiting for {seconds} seconds!")
    sleep(seconds)
    print(f"Waited for {seconds} seconds!")
    return f"Waited for {seconds} seconds!"


def do_it_with_threads() -> List[str]:
    pool = ThreadPool(MAX_POOL)
    results: List[str] = []
    for i in RRANGE:
        results.append(pool.apply_async(wait, (i,)))

    return [r.get() for r in results]


def do_it_without_threads() -> List[str]:
    results: List[str] = []
    for i in RRANGE:
        results.append(wait(i))
    return results


def main():
    print("Starting first step")
    st_with_threds: datetime = datetime.now()
    result_with_threads = do_it_with_threads()
    print(f"Elapsed {datetime.now() - st_with_threds}")

    print("Starting second step")
    st_without_threds: datetime = datetime.now()
    result_without_threads = do_it_without_threads()
    print(f"Elapsed {datetime.now() - st_without_threds}")

    print(f"Result with Threads: '{result_with_threads}'.")
    print(f"Result with Threads: '{result_without_threads}'.")


if __name__ == "__main__":
    main()
