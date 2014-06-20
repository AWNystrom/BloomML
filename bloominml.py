#Needs this: https://github.com/jaybaird/python-bloomfilter
from pybloom import BloomFilter
from time import time
from numpy import inf

class BloomFreqMap:
	def __init__(self, initial_capacity=5000, initial_error_rate=0.0001):
		self.bf = BloomFilter(capacity=initial_capacity, error_rate=initial_error_rate)
	
	def count(self, item):
	#TODO this is a linear time lookup. You can do better O(log(n))
		c = 1
		while self.bf.__contains__(item+'_'+str(c)):
			c += 1
		return c-1
	
	def fancy_count(self, item):
		if not self.bf.__contains__(item+'_'+str(1)):
			return 0
		#Find upper and lower bounds
		c = 1
		while self.bf.__contains__(item+'_'+str(c)):
			c *= 2
		upper = c
		lower = c/2
		while True:
			mid = lower + (upper-lower)/2
			if self.bf.__contains__(item+'_'+str(mid)) and not self.bf.__contains__(item+'_'+str(mid+1)):
				return mid
			#Which side to follow?
			if self.bf.__contains__(item+'_'+str(mid)):
				#Go up
				lower = mid + 1
			else:
				upper = mid - 1
		#We should never be here
		assert 2+2==5
		
	def increment(self, item):
		cur_count = self.fancy_count(item)
		#print 'We have', cur_count
		self.bf.add(item + '_'+ str(cur_count+1), skip_check=True)

class BloomMultinomiamNaiveBayes:
	def __init__(self, alpha):
		self.alpha = alpha
		self.bfm = BloomFreqMap()
		self.class_freqs = {}
		self.token_type_counting_bf = BloomFilter(capacity=initial_capacity, error_rate=initial_error_rate)
		
	def fit(self, tokens, class_label):
		for token in tokens:
			token_type_counting_bf.add(token, skip_check=False)
			key = token + '_' + str(class_label)
			self.bfm.increment(key)
		self.class_freqs[class_label] = self.class_freqs.get(class_label, 0)
	
	def predict(self, tokens):
		max_class, max_score = None, -inf
		for class_label in self.class_freqs:
			for token in tokens:
				
		
if __name__ == '__main__':
	bfm = BloomFreqMap()
	print bfm.count('andrew')
	t1 = time()
	for i in xrange(2000):
		bfm.increment('andrew')
	print bfm.count('andrew')
	t2 = time()
	print t2-t1