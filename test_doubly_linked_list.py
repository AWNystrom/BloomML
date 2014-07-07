#Empty
#Full
#Empty to full

"""
Cases to Test

Insert to head 4 times. Test for length and proper order.

Insert to tail 4 times. Test for length and proper order.

Alternate between inserting to head and tail 4 times each, check for length 
and proper order. Do once starting with each insertion method.



"""

import unittest

from doubly_linked_list import DoublyLinkedList

class TestDoublyLinkedList(unittest.TestCase):

	def setUp(self):
		pass		
		
	def test_creation(self):
		l = DoublyLinkedList()
		self.assertIsInstance(l, DoublyLinkedList)
		self.assertIs(l.size, 0)
	
	def test_addToHead(self):
		l = DoublyLinkedList()
		for i in xrange(4):
			self.assertIs(l.size, i)
			l.addToHead(i)
			self.assertEqual(list(l), range(i, -1, -1))
			
	def test_addToTail(self):
		l = DoublyLinkedList()
		for i in xrange(4):
			self.assertIs(l.size, i)
			l.addToTail(i)
			self.assertEqual(list(l), range(0, i+1))
			
	def test_AddToHead_and_addToTail(self):
		l = DoublyLinkedList()
		sanity = []
		for i in xrange(8):
			if i % 2 == 0:
				l.addToHead(i)
				sanity = [i] + sanity
			else:
				l.addToTail(i)
				sanity.append(i)
			self.assertEqual(list(l), sanity)
		
		l = DoublyLinkedList()
		sanity = []
		for i in xrange(8):
			if i % 2 == 1:
				l.addToHead(i)
				sanity = [i] + sanity
			else:
				l.addToTail(i)
				sanity.append(i)
			self.assertEqual(list(l), sanity)
		

if __name__ == '__main__':
	#suite = unittest.TestLoader().loadTestsFromTestCase(TestDoublyLinkedList)
	#unittest.TextTestRunner(verbosity=2).run(suite)
	unittest.main()