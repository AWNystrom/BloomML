#TODO keep a separate bloom filter that learns which lookups to use binear search on.
#When the frequency reaches some threshold, you know to switch from linear scan.

#Needs this: https://github.com/jaybaird/python-bloomfilter
#from pybloom import BloomFilter
from time import time
from numpy import inf, log
from code import interact

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
	def __init__(self, initial_capacity=500000, initial_error_rate=0.0001):
		self.initial_capacity = initial_capacity
		self.initial_error_rate = initial_error_rate
		self.bf = BloomFilter(capacity=initial_capacity, error_rate=initial_error_rate)
		self.bin_search_cutoff = self.determine_lookup_speed_threshold()
		
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

class BloomMultinomiamNaiveBayes:
	def __init__(self, alpha, initial_capacity, error_rate):
		self.initial_capacity = initial_capacity
		self.error_rate = error_rate
		self.alpha = alpha
		
		#Tracks count | class for p(x|c)
		self.class_conditional_counts = {}#BloomFreqMap()
		
		#Tracks count all tokens | class for p(x|c)
		self.tokens_per_class = {}
		
		#Tracks count(class) for p(c)
		self.class_freqs = {}
		
		#Counts vocab size for smoothing
		self.token_type_bf = BloomFilter(capacity=initial_capacity, error_rate=error_rate)
		
		#Tracks the tokens in each class so that we can penalize unseen tokens
		#self.class_to_toks_bf = {}
	
	def makeTokenFreqmap(self, tokens):
		f = {}
		get = f.get
		for token in tokens:
			f[token] = get(token, 0) + 1
		return f
		
	def fit(self, tokens, class_label):
		#if class_label not in self.class_to_toks_bf:
		#	self.class_to_toks_bf[class_label] = BloomFilter(capacity=self.initial_capacity, error_rate=self.error_rate)
		
		if class_label not in self.class_conditional_counts:
			self.class_conditional_counts[class_label] = BloomFreqMap(initial_capacity=self.initial_capacity, initial_error_rate=self.error_rate)
			
		self.tokens_per_class[class_label] = self.tokens_per_class.get(class_label, 0) + len(tokens)
		tok_freqs = self.makeTokenFreqmap(tokens)
		conditional_counts_bf = self.class_conditional_counts[class_label]
		
		for token, token_freq in tok_freqs.iteritems():
			#self.class_to_toks_bf[class_label].add(token)
			self.token_type_bf.add(token)
			conditional_counts_bf.increment(token, by=token_freq)
			
		self.class_freqs[class_label] = self.class_freqs.get(class_label, 0) + 1
	
	def predict(self, tokens, tie_breaker='highest_freq', use_class_prior=True):
			
		max_class, max_score = None, -inf
		tok_freqs = self.makeTokenFreqmap(tokens)
		num_instances = sum((item[1] for item in self.class_freqs.iteritems()))
		vocab_size = len(self.token_type_bf)
		for class_label, class_freq in self.class_freqs.iteritems():
#			print class_label
			this_score = 0.0
#			print 'prob_c', prob_c
			tok_count_c = self.tokens_per_class[class_label]
			for token, freq in tok_freqs.iteritems():
				count_in_c = self.class_conditional_counts[class_label].count(token)
				if count_in_c == 0:
					continue
				this_score += freq*(log(count_in_c + self.alpha) - log(tok_count_c + vocab_size))
#				print class_label, token, theta_t_c
			
			#Penalize unseen tokens
			#unseen = len(self.class_to_toks_bf[class_label]) - len(tok_freqs)
			if use_class_prior:
				this_score += log(class_freq) - log(num_instances)
			
			if this_score > max_score:
				max_score = this_score
				max_class = class_label
		
		return max_class, max_score
		
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
	
def test_nb():
	from os import walk
	print 'Testing nb'
	clf = BloomMultinomiamNaiveBayes(0.01, 500000, 0.0001)
	
	full_filenames = []
	#Get filenames
	for root, dirs, files in walk('data/20news-18828/'):
		for filename in files:
			full_filenames.append(root + '/' + filename)
	print len(full_filenames)
	
	from random import shuffle
	shuffle(full_filenames)
	from re import findall

	training_time = 0	
	for filename in full_filenames:
		toks = findall('[A-Za-z]{3,}', open(filename).read())
		class_label = filename.rsplit('/', 2)[1]
		
		t0 = time()
		clf.fit(toks, class_label)
		t1 = time()
		training_time += t1-t0

	print 'Took', training_time, 'to train'
	while True:
		i = int(raw_input())
		print full_filenames[i]
		print clf.predict(findall('[A-Za-z]{3,}', open(full_filenames[i]).read()))
	#interact(local=locals())
	print 'Done'
	
if __name__ == '__main__':
	test_nb()