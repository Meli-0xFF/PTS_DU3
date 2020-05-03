import aiohttp
import asyncio

LOCAL_HOST = 'http://localhost:'

class Node():
    def __init__(self, port: str):
        self.port = port
        self.neighbours = set()

    async def _init(self):
        self.neighbours = await get_neighbours(self.port)


async def create_node(port: str) -> Node:
    node = Node(port)
    await node._init()
    return node


async def get_neighbours(port: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(LOCAL_HOST + port) as resp:
            return set(str(await resp.text()).split(','))


async def make_edge(v_1: str, v_2: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(LOCAL_HOST + v_1 + '/new', params={'port': v_2}) as resp:
            print(await resp.text())


async def complete_neighbourhood(start):
    root = await create_node(start)
    for n in [await create_node(n) for n in root.neighbours]:
        for v in ((root.neighbours | set([root.port])) - n.neighbours - set([n.port])):
            await make_edge(n.port, v)


async def main():
    await complete_neighbourhood('8034')

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
