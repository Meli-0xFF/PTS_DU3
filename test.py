import asynctest
from asynctest.mock import MagicMock
import client
import threading
import initialize_nodes
import time

graph = set()

class GetNodeNeighbours(MagicMock):
    async def __call__(self, *args, **kwarg):
        global graph
        return set(map(lambda a: a[1], filter(lambda b: b[0] == args[0], graph)))

class MakeEdge(MagicMock):
    async def __call__(self, *args, **kwarg):
        global graph
        graph.add((args[0], args[1]))


class CompleteNeighbourhoodTestCase(asynctest.TestCase):
    def setUp(self):
        global graph
        graph = {('0', '1'), ('0', '2'), ('0', '3')}

    @asynctest.patch('client.get_neighbours', new_callable=GetNodeNeighbours)
    @asynctest.patch('client.make_edge', new_callable=MakeEdge)
    async def test_complete_neighbourhood(self, neighbours_mock, edge_mock):
        global graph
        await client.complete_neighbourhood('0')
        self.assertTrue(('1', '2') in graph)
        self.assertTrue(('1', '3') in graph)
        self.assertTrue(('2', '3') in graph)
        self.assertTrue(('2', '1') in graph)
        self.assertTrue(('3', '1') in graph)
        self.assertTrue(('3', '1') in graph)


class ClimbDegreeTestCase(asynctest.TestCase):
    def setUp(self):
        global graph
        graph = {('0', '1'), ('1', '2'), ('1', '3'),
                 ('2', '3'), ('2', '4'), ('2', '5'),
                 ('5', '1'), ('5', '3'), ('4', '0')}

    @asynctest.patch('client.get_neighbours', new_callable=GetNodeNeighbours)
    @asynctest.patch('client.make_edge', new_callable=MakeEdge)
    async def test_climb_degree(self, neighbours_mock, edge_mock):
        self.assertEqual(await client.climb_degree('0'), '2')


class Distance4TestCase(asynctest.TestCase):
    def setUp(self):
        global graph
        graph = {('0', '1'), ('1', '2'), ('2', '3'), ('3', '4'),
                 ('1', '5'), ('3', '6'), ('5', '6'), ('6', '7'),
                 ('1', '0'), ('3', '2'), ('3', '1')}

    @asynctest.patch('client.get_neighbours', new_callable=GetNodeNeighbours)
    @asynctest.patch('client.make_edge', new_callable=MakeEdge)
    async def test_distance4(self, neighbours_mock, edge_mock):
        self.assertEqual(await client.distance4('0'), {'7', '4'})
        self.assertNotEqual(await client.distance4('0'), {'7', '4', '3'})



class SystemTestCase(asynctest.TestCase):
    def setUp(self):
        global graph
        graph = {(0, 1), (1, 2), (2, 3), (3, 4), (1, 8)}
        HOST = "localhost"
        graph_base = 8030
        graph = {(graph_base+x, graph_base+y) for x,y in graph}
        nodes = {x for y in graph for x in y}
        self.ready = threading.Condition()
        self.done = threading.Condition()
        self.localhost = threading.Thread(target=initialize_nodes.do_stuff, args=(HOST, nodes, graph, self.ready, self.done, ))

    async def test_system(self):
        self.localhost.start()
        with self.ready:
            self.ready.wait()

        self.assertEqual(await client.distance4('8030'), {'8034'})

        self.assertEqual(await client.climb_degree('8031'), '8031')

        await client.complete_neighbourhood('8031')
        node38 = await client.get_neighbours('8038')
        node32 = await client.get_neighbours('8032')
        self.assertTrue('8032' in node38)
        self.assertTrue('8038' in node32)

        with self.done:
            self.done.notify()
        self.localhost.join()


if __name__ == "__main__":
    asynctest.main()
