from random import random
from math import log, floor
from collections import defaultdict
from numpy import array

class Counter(object):
  def __init__(self, base, adjust=True):
    self.b = base
    self.fm = defaultdict(lambda: 0)
    self.encode = lambda c: 1. + floor(log(c, self.b))
    self.decode = lambda q: (self.b**(q-1) + self.b**q - 1) / 2
    self.adjust = adjust
    
  def __setitem__(self, item, val):
    cur = self.__getitem__(item)
    if cur >= val:
      return
    self.increment(item, val-cur)
    
  def __getitem__(self, item):
    return self.decode(self.fm[item])
  
  def increment(self, item, by):
    cur_q = self.fm[item]
    print 'cur_q', cur_q
    new_count = self.decode(cur_q) + by
    print 'new_count', new_count
    new_q = self.encode(new_count)
    print 'new_q', new_q
    self.fm[item] += (new_q-cur_q)
    print 'inced by', new_q-cur_q

    if self.adjust:
      actual_new_count = self.__getitem__(item)
      print 'actual_new_count', actual_new_count
      print new_count, actual_new_count, (self.decode(new_q+1) - self.decode(new_q))
      p = 1.*(new_count-actual_new_count) / (self.decode(new_q+1) - self.decode(new_q))
      print 'p', p
      if random() <= p:
        self.fm[item] += 1

if __name__ == '__main__':
  import matplotlib.pyplot as plt
  from bloom_freqmap import BloomFreqMapSet
  true_counts = [0]
  filters = 20
  a = BloomFreqMapSet(filters, 1.1, cache_size=0)
  my_counts = [a['b']]
  n = 1000
  my_counts = [0 for i in xrange(n+1)]
  iters = 1
  by = 100
  true_counts = by*array([i for i in xrange(n+1)])
  for iter in xrange(1, iters+1):
    print iter
    a = BloomFreqMapSet(filters, 1.1, cache_size=0)
    for i in xrange(1, n+1):
      print true_counts[i]
      my_counts[i] += a['b']
      a['b'] += by
      #a.increase_count('b', 10)
  my_counts = [1.*i/iters for i in my_counts]
  plt.plot(range(n+1), true_counts)
  plt.plot(range(n+1), my_counts)
  plt.show()
  import code; code.interact(local=locals())