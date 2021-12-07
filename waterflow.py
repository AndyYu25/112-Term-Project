import math

#file contains all algorithms used to find the water flow

def getLowestUnvisitedNode(nodeValues: dict, unvisited: set):
    """returns the lowest value in nodeValues with a key that is also in unvisited"""
    lowestNode = None
    lowestNodeVal = float('inf')
    for node in unvisited:
        if nodeValues[node] < lowestNodeVal:
            lowestNode = node
            lowestNodeVal = nodeValues[lowestNode]
    return lowestNode




#Inspiration from https://docs.google.com/presentation/d/1PrMI2N50vFuaUetykBXcZyYIa-q-vgJvd3MvO7rDRQQ/edit?usp=sharing	
#and https://medium.com/basecs/finding-the-shortest-path-with-a-little-help-from-dijkstra-613149fbdc8e#:~:text=Dijkstra's%20algorithm%20can%20be%20used,to%20find%20the%20shortest%20path.
def dijkstraAll(graph:dict, start:str):
    """uses a variant of Dijkstra's algorithm to return the cost of the shortest path
    from the specified node to every other node in the graph as well as the optimal paths
    to each node (stored in previousNdoes as a dictionary"""
    unvisited = set(graph.keys())
    nodeValues = dict()
    previousNodes = dict()
    startNode = start
    for node in unvisited: #initialize node values
        nodeValues[node] = float('inf')
    nodeValues[startNode] = 0
    while unvisited != set():
        currentNode = getLowestUnvisitedNode(nodeValues, unvisited)
        unvisited.remove(currentNode)
        for neighbour in graph[currentNode]:
            #checks if new path has a lower 'cost' than the current cost 
            #to reach the neighbouring node
            if neighbour[1] + nodeValues[currentNode] < nodeValues[neighbour[0]]:
                nodeValues[neighbour[0]] = neighbour[1] + nodeValues[currentNode]
                previousNodes[neighbour[0]] = currentNode

    return nodeValues, previousNodes
#Inspiration from https://docs.google.com/presentation/d/1PrMI2N50vFuaUetykBXcZyYIa-q-vgJvd3MvO7rDRQQ/edit?usp=sharing
def dijkstraPath(graph:dict, start:str, end:str):
    """similar to dijkstraAll, but with a specified end node and returns the path
    and cost to reach the end node"""
    unvisited = set(graph.keys())
    nodeValues = dict()
    previousNodes = dict()
    startNode = start
    for node in unvisited:
        nodeValues[node] = float('inf')
    nodeValues[startNode] = 0
    while unvisited != set():
        currentNode = getLowestUnvisitedNode(nodeValues, unvisited)
        unvisited.remove(currentNode)
        if currentNode == end: break #check if current node is destination node
        for neighbour in graph[currentNode]:
            #checks if new path has a lower 'cost' than the current cost 
            #to reach the neighbouring node
            if neighbour[1] + nodeValues[currentNode] < nodeValues[neighbour[0]]:
                nodeValues[neighbour[0]] = neighbour[1] + nodeValues[currentNode]
                previousNodes[neighbour[0]] = currentNode
    
    path = []
    #backtrack from end to start to find shortest path
    currentNodeBacktrack = end
    while currentNodeBacktrack != start:
        path.insert(0, currentNodeBacktrack)
        currentNodeBacktrack = previousNodes[currentNodeBacktrack]
    return path, nodeValues[end]


def isLocalMin(graph, node):
    """checks if a given node is a local minimum by seeing if all its edge weights 
    are greater than or equal to 1. Since each edge weight represents the change in 
    height and it is based on a scale from 0 to 2, any edge weight greater than 
    1 indicates that the neighboring tile is at a higher elevation"""
    for neighbor in graph[node]:
        if neighbor[1] < 1:
            return False
    return True

def findClosestMin(graph, tile):
    """finds closest local minima, and returns a list of the node IDs
    which are the closest local minima"""
    nodeCost = dijkstraAll(graph, tile)[0]
    allLocalMinima = dict()
    for node in graph.keys():
        if isLocalMin(graph, node):
            allLocalMinima[node] = nodeCost[node]
    minCost = min(allLocalMinima.values())
    #return all local minima with the lowest "cost to traverse"
    return [node for node, cost in allLocalMinima.items() if minCost == cost]




def testWaterflow():
    """test if algorithms actually work"""
    graph = {
        'a': {('b', 7), ('c', 3)},
        'b': {('a', 7), ('c', 1), ('d', 2), ('e', 6)},
        'c': {('a', 3), ('b', 1), ('d', 2)},
        'd': {('c', 2), ('b', 2), ('e', 4)},
        'e': {('d', 4), ('b', 6)},
        }
    assert(dijkstraAll(graph, 'a')==({'a': 0, 'd': 5, 'b': 4, 'c': 3, 'e': 9}, 
                                     {'c': 'a', 'b': 'c', 'd': 'c', 'e': 'd'}))
    assert(dijkstraPath(graph, 'a', 'e')==(['c', 'd', 'e'], 9))
    assert(dijkstraPath(graph, 'a', 'a')==([], 0))
    elevationGraph = {
        'a': {('b', 1.89), ('c', 1.89), ('d', 1.89)}
    }
    assert(isLocalMin(elevationGraph, 'a')==True)
    elevationGraph = {
        'a': {('b', 1), ('c', 1.89), ('d', 1.89)}
    }
    assert(isLocalMin(elevationGraph, 'a')==True)
    elevationGraph = {
        'a': {('b', 0), ('c', 1.89), ('d', 1.89)}
    }
    assert(isLocalMin(elevationGraph, 'a')==False)
testWaterflow()