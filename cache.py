class Node:
	def __init__(self, data):
		self.data = data

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
	def __repr__(self):
		l = []
		temp = self.head
		while temp is not None:
			l.append(temp.data)
			temp = temp.next
		return str(l)

if __name__ == '__main__':
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