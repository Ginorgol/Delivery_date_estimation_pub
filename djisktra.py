
from collections import defaultdict
import sys

class Heap():

	def __init__(self):
		self.array = []
		self.size = 0
		self.pos = []

	def newMinHeapNode(self, v, dist):
		minHeapNode = [v, dist]
		return minHeapNode

	# A utility function to swap two nodes 
	# of min heap. Needed for min heapify
	def swapMinHeapNode(self,a, b):
		t = self.array[a]
		self.array[a] = self.array[b]
		self.array[b] = t

	# A standard function to heapify at given idx
	# This function also updates position of nodes 
	# when they are swapped.Position is needed 
	# for decreaseKey()
	def minHeapify(self, idx):
		smallest = idx
		left = 2*idx + 1
		right = 2*idx + 2

		if left < self.size and self.array[left][1] \
								< self.array[smallest][1]:
			smallest = left

		if right < self.size and self.array[right][1]\
								< self.array[smallest][1]:
			smallest = right

		# The nodes to be swapped in min 
		# heap if idx is not smallest
		if smallest != idx:

			# Swap positions
			self.pos[ self.array[smallest][0] ] = idx
			self.pos[ self.array[idx][0] ] = smallest

			# Swap nodes
			self.swapMinHeapNode(smallest, idx)

			self.minHeapify(smallest)

	# Standard function to extract minimum 
	# node from heap
	def extractMin(self):

		# Return NULL wif heap is empty
		if self.isEmpty() == True:
			return

		# Store the root node
		root = self.array[0]

		# Replace root node with last node
		lastNode = self.array[self.size - 1]
		self.array[0] = lastNode

		# Update position of last node
		self.pos[lastNode[0]] = 0
		self.pos[root[0]] = self.size - 1

		# Reduce heap size and heapify root
		self.size -= 1
		self.minHeapify(0)

		return root

	def isEmpty(self):
		return True if self.size == 0 else False

	def decreaseKey(self, v, dist):

		i = self.pos[v]
		self.array[i][1] = dist
		while i > 0 and self.array[int(i)][1] < self.array[int((i - 1) / 2)][1]:

			# Swap this node with its parent
			self.pos[ self.array[i][0] ] = int((i-1)/2)
			self.pos[ self.array[int((i-1)/2)][0] ] = i
			self.swapMinHeapNode(i, int((i - 1)/2) )

			# move to parent index
			i = int((i - 1) / 2);
	def isInMinHeap(self, v):

		if self.pos[v] < self.size:
			return True
		return False


def printArr(dist, n):
	print ("Vertex\tDistance from source")
	for i in range(n):
		print ("%d\t\t%d" % (i,dist[i]))


class Graph():

	def __init__(self, V):
		self.V = V
		self.graph = defaultdict(list)

	# Adds an edge to an undirected graph
	def addEdge(self, src, dest, weight):
		newNode = [dest, weight]
		self.graph[src].insert(0, newNode)

	def print_graph(self):
		for src in self.graph:
			print(src)
			for des in self.graph[src]:
				print((des[0],des[1]),end=" ")

	def dijkstra(self, src,des):
		print("*******************")
		print(src)
		print(des)
		print("*****************")
		temp_des=des
		V = self.V # Get the number of vertices in graph
		dist = [] # dist values used to pick minimum 
					# weight edge in cut
		parent={}
		parent[src]=src		
		# minHeap represents set E
		minHeap = Heap()

		# Initialize min heap with all vertices. 
		# dist value of all vertices
		for v in range(V):
			dist.append(sys.maxsize)
			minHeap.array.append( minHeap.newMinHeapNode(v, dist[v]) )
			minHeap.pos.append(v)
		minHeap.pos[src] = src
		dist[src] = 0
		minHeap.decreaseKey(src, dist[src])
		minHeap.size = V;
		while minHeap.isEmpty() == False:
			newHeapNode = minHeap.extractMin()
			u = newHeapNode[0]
			for pCrawl in self.graph[u]:

				v = pCrawl[0]
				if minHeap.isInMinHeap(v) and dist[u] != sys.maxsize and \
				pCrawl[1] + dist[u] < dist[v]:
						# if(v==des):
						# 	#print("here")
						# 	#print(u,pCrawl[1])
						parent[v]=u
						dist[v] = pCrawl[1] + dist[u]
						minHeap.decreaseKey(v, dist[v])

		path=[]		
		while(parent[des]!=des):
			path.append(des)
			des=parent[des]
		
		print(path)

		printArr(dist,V)
		return dist[temp_des]
