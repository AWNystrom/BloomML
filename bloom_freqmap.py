#(COMPLETE) keep a separate bloom filter that learns which lookups to use binear search on.
#When the frequency reaches some threshold, you know to switch from linear scan.

#TODO to minimize errors from using abinary search, stipulate that the k leftmost elements 
#from mid must be in the set, not just the one on the left

#(COMPLETE) A hashtable that points from item to a linked list node. When the cache is added to, 
#the tail of the linked list is removed and the new item is added in its place. 

#Needs this: https://github.com/jaybaird/python-bloomfilter
#from pybloom import BloomFilter
from time import time
from numpy import inf, log
from code import interact

#Needs https://github.com/axiak/pybloomfiltermmap
#10X faster!
from pybloomfilter import BloomFilter
from cache import LRUCache

class BloomFreqMap:
	def __init__(self, initial_capacity=500000, initial_error_rate=0.001, cache_size=5000):
		self.initial_capacity = initial_capacity
		self.initial_error_rate = initial_error_rate
		self.bf = BloomFilter(capacity=initial_capacity, error_rate=initial_error_rate)
		self.bin_search_cutoff = self.determine_lookup_speed_threshold()
		self.cache = LRUCache(cache_size)
		
		#Holds tokens that have at least the threshold number of tokens for which binary 
		#search is faster than linear scan
		self.binsearch_bf = BloomFilter(capacity=initial_capacity, error_rate=initial_error_rate)
		
		self.actual_counts = {} #For testing
	
	def linear_scan_count(self, item):
		bf = self.bf
		c = 1
		while item+'_'+str(c) in bf:
			c += 1
		return c-1
	
	def binsearch_count(self, item):
		bf = self.bf
		if item+'_'+str(1) not in bf:
			return 0
		#Find upper and lower bounds
		c = 1
		while item+'_'+str(c) in bf:
			c *= 2
		upper = c
		lower = c/2
		while True:
			mid = lower + (upper-lower)/2
			if item+'_'+str(mid) in bf and item+'_'+str(mid+1) not in bf:
				return mid
			#Which side to follow?
			if item+'_'+str(mid) in bf:
				#Go up
				lower = mid + 1
			else:
				upper = mid - 1
		#We should never be here
		assert 2+2==5
		
	def count(self, item):
		#See if we've reached the threshold for which a binary search lookup becomes faster
		#If so, use that method. Else use a linear scan.
		
		#search_method = self.binsearch_count if item in self.binsearch_bf else self.linear_scan_count
		search_method = self.linear_scan_count
		result = self.cache.lookup(item, search_method)
		return result
		
	def increment(self, item, by=1):
		"""
		Increment the frequency of item by the amount "by" (default 1).
		"""
		
		cur_count = self.count(item)
		
		if cur_count+1 == self.bin_search_cutoff:
			self.binsearch_bf.add(item)
		
		for i in xrange(cur_count+1, cur_count+by+1):
			self.bf.add(item + '_'+ str(i))
		
		self.cache.update(item, lambda f: f+by)
				
	def determine_lookup_speed_threshold(self):
		from time import time
		#do each one 5 times
		bf = BloomFilter(capacity=self.initial_capacity, error_rate=self.initial_error_rate)
		count = 1
		repetitions = 5
		
		self_bf_holder = self.bf
		self.bf = bf
		while True:
			bf.add('andrew_' + str(count))
			bin_faster_count = 0
			for j in xrange(repetitions):
				#Linear scan
				t1 = time()
				self.linear_scan_count('andrew')
				t2 = time()
				linear_time = t2-t1
			
				t1 = time()
				self.binsearch_count('andrew')
				t2 = time()
				bin_time = t2-t1
			
				bin_faster_count += int(bin_time < linear_time)
		
			if 1.*bin_faster_count / repetitions >= 0.75:
				del bf
				self.bf = self_bf_holder
				return count
			
			count += 1


		
def test_bfm():
	print 'Testing bfm'
	bfm = BloomFreqMap()
	print bfm.count('andrew')
	for i in xrange(200):
		bfm.increment('andrew')
		assert bfm.count('andrew') == i+1
	print bfm.count('andrew')
	bfm.increment_to('andrew', 9001)
	print bfm.count('andrew')
	bfm.increment('andrew', 90)
	print bfm.count('andrew')
	print 'Done'
	
if __name__ == '__main__':
	test_bfm()