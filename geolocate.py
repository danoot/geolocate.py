import math, random

class geolocate():
	__slots__ = ('geodb')

	def __init__(self,fname=None):

		files = {'all':'all_geolocate_data',
			'internal':'internal_geolocate_data',
			'world':'world_geolocate_data'
		}
		try:
			fname = files[fname]
		except KeyError:
			fname = files['all']

		values = []
		with open(fname) as f:
			for l in f.readlines():
				c = l.strip('\n').split('\t')
				values.append((int(c[0]),int(c[1]),c[2]))
		self.geodb = skiplist(values,iplookup=True)

	def get(self,ip):
		a,b,c,d = ip.split('.')
		a = (int(a) * 256**3)
		b = (int(b) * 256**2)
		c = (int(c) * 256)
		d = int(d)
		return self.geodb.next(a+b+c+d)
		
	def get_int(self,ip):
		return self.geodb.next(ip)


class skiplist(object):
	"""Doubly linked non-indexable skip list, providing logarithmic insertion
	and deletion. Keys are any orderable Python object.

		`maxsize`:
			Maximum number of items expected to exist in the list. Performance
			will degrade when this number is surpassed.
	"""
	__slots__ = ('max_level','level','head','nil','tail','_update','p')
	def __init__(self, *args, **kwargs):
		maxsize = 200000
		if args and type(args[0]) in (int,long):
			maxsize = args[0]
			args = args[1:]

		self.max_level = int(math.log(maxsize, 2))
		self.level = 0
		self.head = self._makeNode(self.max_level, None, None)
		self.nil = self._makeNode(-1, None, None)
		self.tail = self.nil
		self.head[3:] = [self.nil for x in xrange(self.max_level)]
		self._update = [self.head] * (1 + self.max_level)
		self.p = 1/math.e
		if kwargs and kwargs['iplookup']:
			#update values but permafy the surrounding values, so we don't get leakages.
			print "hi"
			for i in args:
				self.update2(i)
		else:
			for i in args:
				self.update(i)
			self.update(kwargs)

	def _makeNode(self, level, key, value):
		node = [None] * (4 + level)
		node[0] = key
		node[1] = value
		return node

	def _randomLevel(self):
		lvl = 0
		max_level = min(self.max_level, self.level + 1)
		while random.random() < self.p and lvl < max_level:
			lvl += 1
		return lvl

	def items(self, searchKey=None, reverse=False):
		"""Yield (key, value) pairs starting from `searchKey`, or the next
		greater key, or the end of the list. Subsequent iterations move
		backwards if `reverse=True`. If `searchKey` is ``None`` then start at
		either the beginning or end of the list."""
		if reverse:
			node = self.tail
		else:
			node = self.head[3]
		if searchKey is not None:
			update = self._update[:]
			found = self._findLess(update, searchKey)
			if found[3] is not self.nil:
				node = found[3]
		idx = 2 if reverse else 3
		while node[0] is not None:
			yield node[0], node[1]
			node = node[idx]
			
	def update2(self,d):
		for k1,k2,v in d:
			v1 = self.next(k1-1)
			v2 = self.next(k2+1)
			self[k1-1] = v1
			self[k1] = v
			self[k2] = v
			self[k2+1] = v2

	def update(self,d=None,**e):
		if hasattr(d,'__iter__') and callable(d.__iter__):
			if hasattr(d,'items') and callable(d.items):
				d = d.items()
			for k,v in d:
				self[k]=v
		for k,v in e.items():
			self[k]=v

	def __iter__(self):
		return self.keys()

	def __len__(self):
		return len(tuple(self.keys()))

	def keys(self):
		return (k for k,v in self.items())

	def values(self):
		return (v for k,v in self.items())

	def next(self,skey):
		node = self.tail
		update = self._update[:]
		found = self._findLess(update,skey)
		if found[3] is not self.nil:
				node = found[3]
		return node[1]

	def _findLess(self, update, searchKey):
		node = self.head
		for i in xrange(self.level, -1, -1):
			key = node[3 + i][0]
			while key is not None and key < searchKey:
				node = node[3 + i]
				key = node[3 + i][0]
			update[i] = node
		return node

	def __setitem__(self, searchKey, value):
		"""Insert `searchKey` into the list with `value`. If `searchKey`
		already exists, its previous value is overwritten."""
		assert searchKey is not None
		update = self._update[:]
		node = self._findLess(update, searchKey)
		prev = node
		node = node[3]
		if node[0] == searchKey:
			node[1] = value
		else:
			lvl = self._randomLevel()
			self.level = max(self.level, lvl)
			node = self._makeNode(lvl, searchKey, value)
			node[2] = prev
			for i in xrange(0, lvl+1):
				node[3 + i] = update[i][3 + i]
				update[i][3 + i] = node
			if node[3] is self.nil:
				self.tail = node
			else:
				node[3][2] = node

	def __delitem__(self, searchKey):
		"""Delete `searchKey` from the list, returning ``True`` if it
		existed."""
		update = self._update[:]
		node = self._findLess(update, searchKey)
		node = node[3]
		if node[0] == searchKey:
			node[3][2] = update[0]
			for i in xrange(self.level + 1):
				if update[i][3 + i] is not node:
					break
				update[i][3 + i] = node[3 + i]
			while self.level > 0 and self.head[3 + self.level][0] is None:
				self.level -= 1
			if self.tail is node:
				self.tail = node[2]
			return True

	def __getitem__(self, searchKey):
		"""Return the value associated with `searchKey`, or ``None`` if
		`searchKey` does not exist."""
		node = self.head
		for i in xrange(self.level, -1, -1):
			key = node[3 + i][0]
			while key is not None and key < searchKey:
				node = node[3 + i]
				key = node[3 + i][0]
		node = node[3]
		if node[0] == searchKey:
			return node[1]

	def __contains__(self, key):
		return self[key] is not None

def loads(s,sp=None,reverse=False):
	l = skiplist()
	for i in (x.strip().split(sp,1) for x in s.strip().replace('\r','').split('\n')):
		l[i[0^reverse]]=i[1^reverse]
	return l

def load(filename,sp=None,reverse=False):
	with file(filename) as f:
		return loads(f.read(),sp,reverse)


