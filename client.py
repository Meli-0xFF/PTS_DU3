import aiohttp
import asyncio

LOCAL_HOST = 'http://localhost:'


class Node():
    def __init__(self, port: str):
        self.port = port
        self.neighbours = set()

    async def _init(self):
        self.neighbours = await get_neighbours(self.port)


async def get_node(port: str) -> Node:
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
    root = await get_node(start)
    for n in [await get_node(n) for n in root.neighbours]:
        for v in (root.neighbours - n.neighbours - set([n.port]) - set([root.port])):
            await make_edge(n.port, v)

async def climb_degree(start):
    root = await get_node(start)
    degrees = {len(n.neighbours):n.port for n in [await get_node(n) for n in sorted(root.neighbours, key=int, reverse=True)]}

    if len((await get_node(degrees.get(max(degrees)))).neighbours) < len(root.neighbours): return start
    else : return await climb_degree(degrees.get(max(degrees)))


async def bfs(start, used: dict, dist: int):
    root = await get_node(start)

    if used.get(root.port) is None: used[root.port] = dist

    if dist < 4:
        for node in root.neighbours:
            if used.get(node) is None: used[node] = used[root.port]+1
    else: return

    for node in root.neighbours:
        await bfs(node, used, dist+1)


async def distance4(start):
    used_nodes = {}
    await bfs(start, used_nodes, 0)
    return set(map(lambda a: a[0], set(filter(lambda x: x[1] == 4, used_nodes.items()))))


async def main():
    print(await distance4('8034'))

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
