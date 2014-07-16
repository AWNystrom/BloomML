#Needs this: https://github.com/jaybaird/python-bloomfilter
from pybloom import BloomFilter

from time import time
from math import log
#Needs https://github.com/axiak/pybloomfiltermmap
#10X faster!
#from pybloomfilter import BloomFilter
from lru_cacher import LruCacher

from code import interact

def log_encoder(base=1.5):
	return lambda n: int(1.0 + int(log(n, base)))
def log_decoder(base=1.5):
	return lambda n: int(round(1.0*(base**n + base**(n-1) - 1) / 2))

class BloomFreqMap:
	def __init__(self, bloom_size=500000, bloom_error=0.001, cache_size=5000, 
				 encoder=lambda item: item, decoder=lambda item: item, 
				 bin_search_lookback=3):
		"bloom_size: the number of elements that can be stored in the"
		"    internal bloom filter while keeping the specified error"
		"    rate."
		"bloom_error: the max error rate of the bloom filter so long as"
		"    at most bloom_size are stored."
		"cache_size: the max size of the internal LRU cache."
		"encoder: when a count n is stored, we insert 1-n into the"
		"    bloom filter. This can take up a lot of the bloom filter's"
		"    space for large n. Instead, we can store a transformed"
		"    version of n to squash it, reqiring fewer insertions"
		"    (e.g. 1+int(log_b(n))) and perform an inverse when we read"
		"    it back out (e.g. (b^j+b^(j+1)-1)/2 where j is the result"
		"    of the example encoder). The squashing function is the"
		"    encoder. log_encoder is a good choice. See D Talbot,"
		"    M Osborne - EMNLP-CoNLL, 2007 for more information."
		"decoder: see explanation of encoder. decoder is the inverse of"
		"    the squasher. log_decoder is a good choice."
		"bin_search_lookback: when a binary search is performed to find"
		"    the frequency, don't just ensure that we've found a"
		"    situation in which mid is in the bloom fliter and mid+1"
		"    isn't, but also check this many to the left of mid."
		self.bloom_size = bloom_size
		self.bloom_error = bloom_error
		self.bf = BloomFilter(capacity=bloom_size, error_rate=bloom_error)
		self.encoder = encoder
		self.decoder = decoder
		self.cache = LruCacher(cache_size, self.plan_b_count)
		
		#Holds tokens that have at least the threshold number of tokens for which binary 
		#search is faster than linear scan
		self.binsearch_bf = BloomFilter(capacity=bloom_size, error_rate=bloom_error)
		self.bin_search_lookback = bin_search_lookback
		self.bin_search_cutoff = self.determine_lookup_speed_threshold()
		print self.bin_search_cutoff
	
	def linear_scan_count(self, item):
		print 'linear searching'
		bf = self.bf
		c = 1
		while item+'_'+str(c) in bf:
			c += 1
		c -= 1
		return self.decoder(c)
	
	def binsearch_count(self, item):
		print 'binary searching'
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
		return search(item)
		
	def count(self, item):		
		result, _ = self.cache.lookup(item)
		return result
	
	def __getitem__(self, item):
		return self.count(item)
	
	def __setitem__(self, item, val):
		cur_count = self.count(item)
		if val < cur_count:
			raise RuntimeWarning("Cannot decrease count of " + item + " from " + \
								 str(cur_count) + " to " + str(val))
			return
		self.increment(item, val-cur_count)
		
	def increment(self, item, by=1):
		"""
		Increment the frequency of item by the amount "by" (default 1).
		"""
		
		est_cur_count = self.count(item)
		new_count = self.encoder(est_cur_count + by)
		
		if est_cur_count+by >= self.bin_search_cutoff:
			self.binsearch_bf.add(item)
		
		for i in xrange(est_cur_count+1, new_count+1):
			self.bf.add(item + '_'+ str(i))
		
		self.cache.update(item, new_count)
				
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
			