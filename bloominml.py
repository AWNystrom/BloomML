#TODO keep a separate bloom filter that learns which lookups to use binear search on.
#When the frequency reaches some threshold, you know to switch from linear scan.

#Needs this: https://github.com/jaybaird/python-bloomfilter
#from pybloom import BloomFilter
from time import time
from numpy import inf

#Needs https://github.com/axiak/pybloomfiltermmap
#10X faster!
from pybloomfilter import BloomFilter

#You could use one filter for each class, which might allow you to do some interesting things...

class Cache:
	def __init__(self, max_size):
		self.max_size = max_size
		
	def __contains__(self, item):
		print 'Yo yo yo', item

class BloomFreqMap:
	def __init__(self, initial_capacity=5000, initial_error_rate=0.0001):
		self.initial_capacity = initial_capacity
		self.initial_error_rate = initial_error_rate
		self.bf = BloomFilter(capacity=initial_capacity, error_rate=initial_error_rate)
		self.bin_search_cutoff = self.determine_lookup_speed_threshold()
		
		self.binsearch_bf = BloomFilter(capacity=initial_capacity, error_rate=initial_error_rate)
	
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
		print 'upper, lower', upper, lower
		while True:
			mid = lower + (upper-lower)/2
			print 'Mid', mid
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
		return self.linear_scan_search(item, bf=bf)
		
	def increment(self, item, binsearch=False):
		"""
		If binsearch is true, the count of an item is found via a binary search.
		If it's false, a linear scan is used from 1 to n. The former is more efficient for
		large counts, the latter for small.
		"""
		cur_count = self.binsearch_count(item) if binsearch else self.linear_scan_count(item)
		
		if cur_count+1 == self.bin_search_cutoff:
			self.binsearch_bf.add(item)
			
		self.bf.add(item + '_'+ str(cur_count+1))
		
	def determine_lookup_speed_threshold(self):
		from time import time
		#do each one 5 times
		bf = BloomFilter(capacity=self.initial_capacity, error_rate=self.initial_error_rate)
		count = 1
		repetitions = 5
		while True:
			bf.add('andrew_' + str(count))
		
			bin_faster_count = 0
			print 'Trying for', count
			for j in xrange(repetitions):
				print 'j =', j
				#Linear scan
				t1 = time()
				print 'Starting scan'
				self.linear_scan_count('andrew', bf)
				print 'Done with scan'
				t2 = time()
				linear_time = t2-t1
			
				t1 = time()
				print 'Starting bin search'
				self.binsearch_count('andrew', bf)
				print 'Ending bin search'
				t2 = time()
				bin_time = t2-t1
			
				bin_faster_count += int(bin_time < linear_time)
		
			if 1.*bin_faster_count / repetitions >= 0.75:
				return count
			
			count += 1

class BloomMultinomiamNaiveBayes:
	def __init__(self, alpha):
		self.alpha = alpha
		self.bfm = BloomFreqMap()
		self.class_freqs = {}
		self.token_type_counting_bf = BloomFilter(capacity=initial_capacity, error_rate=initial_error_rate)
		
	def fit(self, tokens, class_label):
		for token in tokens:
			token_type_counting_bf.add(token)
			key = token + '_' + str(class_label)
			self.bfm.increment(key)
		self.class_freqs[class_label] = self.class_freqs.get(class_label, 0) + 1
	
	def predict(self, tokens):
		token_freqmap = {}
		for token in tokens:
			token_freqmap[token] = token_freqmap.get(token, 0.) + 1
			
		max_class, max_score = None, -inf
		for class_label in self.class_freqs:
			this_score = 1.0
			this_class_freq = self.class_freqs[class_label]
			for token in token_freqmap:
				key = token + '_' + str(class_label)
				token_freq_in_class = 1.*self.bfm.count(key)
				this_score *= token_freq_in_class / this_class_freq
				
			#Now penalize for all unseen tokens
			u = len() - len()#unseen count
			this_score /= self.alpha**u/this_class_freq**u
			if this_score > max_score:
				max_score = this_score
				max_class = class_label
		return max_class
				
if __name__ == '__main__':
	bfm = BloomFreqMap()
	x = bfm.
	print 'At', x, 'binsearch_count becomes faster'
	from sys import exit
	exit(0)
	print bfm.binsearch_count('andrew')
	t1 = time()
	for i in xrange(2000):
		bfm.increment('andrew')
	print bfm.binsearch_count('andrew')
	t2 = time()
	print t2-t1