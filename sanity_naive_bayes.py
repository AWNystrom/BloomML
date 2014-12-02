from collections import defaultdict
from numpy import inf
from math import log

def make_freqmap(tokens):
	freqmap = defaultdict(lambda:0)
	for t in tokens:
		freqmap[t] += 1
	return freqmap
		
class MNB(object):
	def __init__(self, alpha):
		self.c_tok_to_f = defaultdict(lambda:defaultdict(lambda:0))
		self.c_f = defaultdict(lambda:0)
		self.vocab = set()
		self.alpha = alpha
		self.n = 0
		self.c_to_toks_count = defaultdict(lambda:0)
			
	def fit(self, freqmap, c):
		
		for t, f in freqmap.iteritems():
			self.c_tok_to_f[c][t] += f
			self.vocab.add(t)
			self.c_to_toks_count[c] += f
			
		self.c_f[c] += 1
		self.n += 1
	
	def predict(self, freqmap):
		best_score_class_pair = (-inf, None)
		
		for c, c_freq in self.c_f.iteritems():
			score = log(c_freq) - log(self.n)
			for t, t_f in freqmap.iteritems():
				score += log(self.c_tok_to_f[c][t]+self.alpha) - \
						 log(len(self.vocab) + self.c_to_toks_count[c])
			best_score_class_pair = max(best_score_class_pair, (score, c))
		return (best_score_class_pair[1], best_score_class_pair[0])
	
	def bernoulli_predict(self, freqmap):
		best_score_class_pair = (-inf, None)
		
		for c, c_freq in self.c_f.iteritems():
			score = log(c_freq) - log(self.n)
			for t, t_f in freqmap.iteritems():
				score += log(self.c_tok_to_f[c][t]+self.alpha) - \
						 log(len(self.vocab) + self.c_to_toks_count[c])
					 
			for t in set(self.c_tok_to_f[c].keys()).difference(freqmap.keys()):
				score += -log(self.c_tok_to_f[c][t]+self.alpha) - \
							 log(len(self.vocab) + self.c_to_toks_count[c])
			best_score_class_pair = max(best_score_class_pair, (score, c))
		return (best_score_class_pair[1], best_score_class_pair[0])
