from code import interact

class Node:
	def __init__(self, data):
		self.data = data
		self.next = None
		self.prev = None
		
class DoublyLinkedList:
	def __init__(self):
		self.head = None
		self.tail = None
		self.size = 0
	def addToTail(self, data):
		node = Node(data)
		if self.tail is None:
			self.head = node
			self.tail = node
			node.next = None
			node.prev = None
		else:
			self.tail.next = node
			node.prev = self.tail
			node.next = None
			self.tail = node
		self.size += 1
	def addToHead(self, data):
		node = Node(data)
		if self.head is None:
			self.head = node
			self.tail = node
			node.next = None
			node.prev = None
		else:
			self.head.prev = node
			node.next = self.head
			node.prev = None
			self.head = node
		self.size += 1
	def removeTail(self):
		if self.tail is None:
			return
		temp = self.tail
		if self.tail.prev is not None:
			self.tail = self.tail.prev
			self.tail.next = None
		else:
			self.head = None
			self.tail = None
		del temp
		self.size -= 1
		
	def moveToHead(self, node):
		"""
		Move some node that's already in the list to the head. The method 
		assumes the node is in the list - no check is made. Proper use is in
		the user's hands. The head and everything between the item being 
		moved to the head gets shifted one to the right.
		"""
		if self.head is node:
			return
			
		if self.tail is node:
			#We know node.prev isn't None since node isn't the head
			self.tail = node.prev
		else:
			node.next.prev = node.prev
			
		node.prev.next = node.next
		
			
		self.head.prev = node
		node.next = self.head
		node.prev = None
		self.head = node
		
	def __repr__(self):
		l = []
		print 'printing'
		temp = self.head
		while temp is not None:
			l.append(temp.data)
			temp = temp.next
		return str(l)
	
	def display(self):
		temp = self.head
		i = 0
		while temp is not None:
			print '*'*80
			print 'i:', i
			print 'temp', temp
			print 'data:', temp.data
			print 'prev:', temp.prev
			print 'next', temp.next
			temp = temp.next
			i += 1
		
class LRUCache:
	def __init__(self, max_size):
		self.max_size = max_size
		self.ht = {}
		self.ll = DoublyLinkedList()
		
	def lookup(self, item, plan_b_func):
		#If the item is in the cache, move it to the front of the linked list
		#then return it. If it's not in the cache, remove the last item in the
		#linked list, queries the plan_b_func for the result, adds it to the 
		#cache, and returns it. This should be a decorator.
		#interact(local=locals()) 
		#data is the count, item is the token
		if item not in self.ht:
			result = plan_b_func(item)
			if len(self.ht) == self.max_size:
				del self.ht[self.ll.tail.item]
				self.ll.removeTail()
			self.ll.addToHead(result)
			self.ll.head.item = item
			self.ht[item] = self.ll.head
		else:
			#The item was in the cache. Move it to the front of 
			#the linked list.
			node = self.ht[item]
			result = node.data
		
		return result
	
	def update(self, item, func):
		if item not in self.ht:
			return
		
		node = self.ht[item]
		node.data = func(node.data)
		
def test_linked_list():
	l = DoublyLinkedList()
	print l
	l.addToTail(1)
	print l
	l.addToHead(5)
	print l
	l.removeTail()
	print l
	l.removeTail()
	print l
	
	l.addToTail(1)
	l.addToTail(7)
	l.addToTail(3)
	
	print l
	l.moveToHead(l.head)
	print l
	l.moveToHead(l.head.next)
	print l
	l.moveToHead(l.head.next.next)
	l.display()
	print l

def test_cache():
	def calculate(i):
		from time import sleep
		sleep(3)
		return i**2
		
	cache = LRUCache(5)
	interact(local=locals())
	print 'Here?'
	print cache.ll
	cache.lookup(5, calculate)
	print 'Here?'
	cache.lookup(5, calculate)
	print cache.ll
	
	print 'Here?'
	cache.lookup(6, calculate)
	print cache.ll
	print 'Here?'
	cache.lookup(6, calculate)
	print cache.ll

if __name__ == '__main__':
	test_cache()