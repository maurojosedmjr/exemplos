import time
from datetime import datetime
import asyncio
from typing import Dict


def fun1():
    print("Fun1", datetime.now())
    time.sleep(15)
    print("finalizou a Fun1", datetime.now())


def fun2():
    print("Fun2", datetime.now())
    time.sleep(20)
    print("finalizou a Fun2", datetime.now())


def fun3():
    print("Fun3", datetime.now())
    time.sleep(5)
    print("finalizou a Fun3", datetime.now())


async def exec_callable(loop: asyncio.get_event_loop, map_exec: Dict):
    result = []
    for value in map_exec.values():
        result.append(loop.run_in_executor(None, value))
    await asyncio.gather(*result)

    return result


if __name__ == "__main__":
    print("rodando em tempo de execução")
    start = datetime.now()
    fun1()
    fun2()
    fun3()
    end = datetime.now()
    print("Demorou: ", end - start)
    print("rodando async agora")
    map_execs: Dict[str, callable] = {
        "fun1": fun1,
        "fun2": fun2,
        "fun3": fun3,
    }
    loop = asyncio.get_event_loop()
    start = datetime.now()
    result = loop.run_until_complete(
        exec_callable(loop, map_exec=map_execs)
    )
    end = datetime.now()
    print("Demorou: ", end - start)
