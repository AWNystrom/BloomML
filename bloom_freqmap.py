"""

the squashed counts are stored. So the lookup should look like

c = 1
while c in bf:
	c+= 1
return self.decode(c-1)

the increment should look like

def increment(item, by):
	#Get the current quantized count
	cur = count(item, decode=True)
	to = self.encode(cur+by)
	
	for i in xrange(cur+1, to+1):
		bf.add(item+'_'_str(i)) #adding quantized counts
		

"""

#TODO: quantized and binsearch thresh

#Needs this: https://github.com/jaybaird/python-bloomfilter
from pybloom import BloomFilter
from random import random
from time import time
from math import log, floor
import logging
#Needs https://github.com/axiak/pybloomfiltermmap
#10X faster!
#from pybloomfilter import BloomFilter
from lru_cacher import LruCacher
from numpy import median, mean
from code import interact
from scipy.stats.mstats import mquantiles

class BloomFreqMapSet(object):
	def __init__(self, num, b, bloom_size=500000, bloom_error=0.001, 
				 cache_size=500, bin_search_lookback=3, quantum_leap=True):
		self.num = num
		self.b = b
		self.bloom_size = bloom_size
		self.bloom_error = bloom_error
		self.cache_size = cache_size
		self.bin_search_lookback = bin_search_lookback
		self.quantum_leap = quantum_leap
		
		self.bfms = [BloomFreqMap(b, bloom_size, bloom_error, 
															cache_size, bin_search_lookback, 
															quantum_leap) for i in xrange(num)]
															
	def __getitem__(self, item):
		counts = [bfm[item] for bfm in self.bfms]
		return mquantiles(counts, prob=[0.375])[0]
		
	def increase_count(self, item, by):
		for bfm in self.bfms:
			for i in xrange(int(by)):
				bfm.increase_count(item, 1.0)
		
	def __setitem__(self, item, val):
		for bfm in self.bfms:
			bfm.__setitem__(item, val)
				
class BloomFreqMap(object):
	def __init__(self, b, bloom_size=500000, bloom_error=0.001, 
				 cache_size=500, bin_search_lookback=3, quantum_leap=True):
		"bloom_size: the number of elements that can be stored in the"
		"    internal bloom filter while keeping the specified error"
		"    rate."
		"bloom_error: the max error rate of the bloom filter so long as"
		"    at most bloom_size are stored."
		"cache_size: the max size of the internal LRU cache."
		"base: the base of the logarithm used to quantize the counts."
		"      lower values have cause more precise counting, but have"
		"      less compression."
		"bin_search_lookback: when a binary search is performed to find"
		"    the frequency, don't just ensure that we've found a"
		"    situation in which mid is in the bloom fliter and mid+1"
		"    isn't, but also check this many to the left of mid."
		self.bloom_size = bloom_size
		self.bloom_error = bloom_error
		self.bf = BloomFilter(capacity=bloom_size, error_rate=bloom_error)
		self.cache = LruCacher(cache_size, self.plan_b_count)
		self.base = b
		self.adjust = quantum_leap
		
		if b is None:
			self.encode = lambda n: n
			self.decode = lambda n: n
		else:
			self.encode = lambda c: 1.0 + floor(log(c, b))
			self.decode = lambda q: (b**(q-1) + b**q - 1) / 2
		
		
		
		#Holds tokens that have at least the threshold number of tokens for which binary 
		#search is faster than linear scan
		self.binsearch_bf = BloomFilter(capacity=bloom_size, error_rate=bloom_error)
		self.bin_search_lookback = bin_search_lookback
		self.bin_search_cutoff = self.determine_lookup_speed_threshold()
	
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
			if item+'_'+str(mid+1) not in bf and \
			   all(item+'_'+str(i) in bf for i in \
			   	   xrange(mid, max(mid-self.bin_search_lookback-1, 0), -1)):
				return mid
			#Which side to follow?
			if item+'_'+str(mid) in bf:
				#Go up
				lower = mid + 1
			else:
				upper = mid - 1
		#We should never be here
		assert 2+2==5
	
	def plan_b_count(self, item):
		#See if we've reached the threshold for which a binary search lookup becomes faster
		#If so, use that method. Else use a linear scan.
		search = self.binsearch_count if item in self.binsearch_bf else self.linear_scan_count
		result = search(item)
		if result == 0:
			return 0
		return result
	
	def increase_count(self, item, by):
		for i in xrange(int(by)):
			self.increment(item, 1.0)
		
	def count(self, item):
		result, found_in_cache = self.cache.lookup(item)
		return result
	
	def __getitem__(self, item):
		return self.decode(self.count(item))
	
	def __setitem__(self, item, val):
		cur_count = self.__getitem__(item)
		if val < cur_count:
#			logging.warning("Cannot decrease count of " + item + " from " + \
#								 str(cur_count) + " to " + str(val))
			return
		self.increment(item, val-cur_count)
		
	def increment(self, item, by=1):
		"""
		Increment the frequency of item by the amount "by" (default 1).
		"""
		
		cur_q = self.count(item)
		cur_count = self.decode(cur_q)
		new_count = cur_count + by
		new_q = self.encode(new_count)
		quant_inc = new_q-cur_q
		
		for i in xrange(int(cur_q)+1, int(new_q)+1):
			self.bf.add(item + '_'+ str(i))
		self.cache.update(item, new_q) #Not necessary. Just manually calculate it as (b**new_q + b**(new_q-1) - 1) /2
#		print 'inced by', quant_inc
    
		
		if self.adjust:
			actual_new_count = self.__getitem__(item)	#Can you get this without calling this function?
#			print 'actual_new_count', actual_new_count
#			print new_count, actual_new_count, (self.decode(new_q+1) - self.decode(new_q))
			p = 1.*(new_count-actual_new_count) / (self.decode(new_q+1) - self.decode(new_q))
#			print 'p', p
			if random() <= p:
				new_q += 1
				self.bf.add(item + '_'+ str(int(new_q)))
				new_count = self.__getitem__(item)	#Can you get this without calling this function?
		
		if new_q >= self.bin_search_cutoff:
			self.binsearch_bf.add(item)
		
		self.cache.update(item, new_q)
				
	def determine_lookup_speed_threshold(self):
		from time import time
		#do each one 5 times
		bf = BloomFilter(capacity=self.bloom_size, error_rate=self.bloom_error)
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
			