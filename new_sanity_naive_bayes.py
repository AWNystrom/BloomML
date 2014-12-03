from numpy import inf
from math import log

class MultinomialNaiveBayes(object):
	def __init__(self, alpha, priors=True):
	
		#freq tok given class
		self.c_tok_to_f = {}
		
		#Class freqs
		self.c_f = {}
		
		#To get |V| (size of total vocabulary)
		self.vocab = set()
		
		#Lidstone smoothing
		self.alpha = alpha
		
		#Number of instances trained on
		self.n = 0
		
		#Total tokens trained on for each class
		self.c_to_toks_count = {}
		
		self.priors = priors
			
	def fit(self, freqmap, c):
		
		for t, f in freqmap.iteritems():
			if c not in self.c_tok_to_f:
				self.c_tok_to_f[c] = {}
			if t not in self.c_tok_to_f[c]:
				self.c_tok_to_f[c][t] = 0
			self.c_tok_to_f[c][t] += f
			self.vocab.add(t)
			self.c_to_toks_count[c] = self.c_to_toks_count.get(c, 0) + f
			
		self.c_f[c] = self.c_f.get(c, 0) + 1
		self.n += 1
	
	def predict(self, freqmap):
		best_score_class_pair = (None, None)
		
		priors = self.priors
		for c, c_freq in self.c_f.iteritems():
			score = log(c_freq) - log(self.n) if priors else 0.
			for t, t_f in freqmap.iteritems():
				score += log(self.c_tok_to_f[c].get(t, 0)+self.alpha) - \
						 log(len(self.vocab) + self.c_to_toks_count.get(c, 0))
			best_score_class_pair = max(best_score_class_pair, (score, c))
		return (best_score_class_pair[1], best_score_class_pair[0])
