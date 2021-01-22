import asyncio

# exemplo besta de asyncio

def add(n):
    return n[0] + n[1]

async def exec_callable(loop: asyncio.get_event_loop, map_exec: Dict):
    result = []
    for value in map_exec.values():
        result.append(loop.run_in_executor(None, value[0], value[1]))
        print(result)
    for response in await asyncio.gather(*result):
        pass
    return result

map_execs = {
    "a": (add, (1, 3)),
    "b": (add, (8, 1)),
    "c": (add, (4, 2)),
    "d": (add, (1, 1)),
}

loop = asyncio.get_event_loop()

result = loop.run_until_complete(
    exec_callable(loop, map_exec=map_execs)
)

for r in result:
    print(r.result())
