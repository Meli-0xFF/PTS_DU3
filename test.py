import asynctest
from asynctest.mock import MagicMock
import client

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
        global graph
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
        global graph
        self.assertEqual(await client.distance4('0'), {'7', '4'})
        self.assertNotEqual(await client.distance4('0'), {'7', '4', '3'})


if __name__ == "__main__":
    asynctest.main()
