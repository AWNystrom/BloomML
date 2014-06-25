#TODO keep a separate bloom filter that learns which lookups to use binear search on.
#When the frequency reaches some threshold, you know to switch from linear scan.

#TODO to minimize errors from using abinary search, stipulate that the k leftmost elements 
#from mid must be in the set, not just the one on the left

#Needs this: https://github.com/jaybaird/python-bloomfilter
#from pybloom import BloomFilter
from time import time
from numpy import inf, log
from code import interact

#Needs https://github.com/axiak/pybloomfiltermmap
#10X faster!
from pybloomfilter import BloomFilter

#You could use one filter for each class, which might allow you to do some interesting things...

#A hashtable that points from item to a linked list node. When the cache is added to, 
#the tail of the linked list is removed and the new item is added in its place. 
class Cache:
	def __init__(self, max_size):
		self.max_size = max_size
		
	def __contains__(self, item):
		print 'Yo yo yo', item

class BloomFreqMap:
	def __init__(self, initial_capacity=50000000, initial_error_rate=0.0001):
		self.initial_capacity = initial_capacity
		self.initial_error_rate = initial_error_rate
		self.bf = BloomFilter(capacity=initial_capacity, error_rate=initial_error_rate)
		self.bin_search_cutoff = self.determine_lookup_speed_threshold()
		
		#Holds tokens that have at least the threshold number of tokens for which binary 
		#search is faster than linear scan
		self.binsearch_bf = BloomFilter(capacity=initial_capacity, error_rate=initial_error_rate)
		
		self.actual_counts = {} #For testing
	
	def linear_scan_count(self, item, bf=None):
		if bf is None:
			bf = self.bf
		c = 1
		while item+'_'+str(c) in bf:
			c += 1
		return c-1
	
	def binsearch_count(self, item, bf=None):
		if bf is None:
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
		
	def count(self, item, bf=None):
		#See if we've reached the threshold for which a binary search lookup becomes faster
		#If so, use that method. Else use a linear scan.
		if item in self.binsearch_bf:
			return self.binsearch_count(item, bf=bf)
		return self.linear_scan_count(item, bf=bf)
	
	def increment_to(self, item, to):
	
		cur_count = self.binsearch_count(item) if self.binsearch_bf else self.linear_scan_count(item)
		
		if cur_count >= to:
			return
		
		if to >= self.bin_search_cutoff:
			self.binsearch_bf.add(item)
		
		by = to-cur_count
		if by <= 0:
			return
		
		self.increment(item, by=by)
		
	def increment(self, item, by=1):
		"""
		Increment the frequency of item by the amount "by" (default 1).
		"""
		
		cur_count = self.binsearch_count(item) if item in self.binsearch_bf else self.linear_scan_count(item)
		
#		self.actual_counts[item] = self.actual_counts.get(item, 0) + by
		
		if cur_count+1 == self.bin_search_cutoff:
			self.binsearch_bf.add(item)
		
		try:
			for i in xrange(cur_count+1, cur_count+by+1):
				self.bf.add(item + '_'+ str(i))
		except:
			interact(local=locals())
				
	def determine_lookup_speed_threshold(self):
		from time import time
		#do each one 5 times
		bf = BloomFilter(capacity=self.initial_capacity, error_rate=self.initial_error_rate)
		count = 1
		repetitions = 5
		while True:
			bf.add('andrew_' + str(count))
			bin_faster_count = 0
			for j in xrange(repetitions):
				#Linear scan
				t1 = time()
				self.linear_scan_count('andrew', bf)
				t2 = time()
				linear_time = t2-t1
			
				t1 = time()
				self.binsearch_count('andrew', bf)
				t2 = time()
				bin_time = t2-t1
			
				bin_faster_count += int(bin_time < linear_time)
		
			if 1.*bin_faster_count / repetitions >= 0.75:
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