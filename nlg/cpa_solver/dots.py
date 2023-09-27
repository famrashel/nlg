#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

###############################################################################

__author__ = 'Yves Lepage <yves.lepage@waseda.jp>'
__date__ = '14/04/2011' # First version: 2007
__version__ = '1.1'
__description__ = 'Trace dots or a turning bar to keep the user waiting.'

__verbose__ = False

###############################################################################

class Dots:

	def __init__(self, every = 1):
		self.dot = 0
		self.every = every

	def trace(self):
		"""
		Pretty print a self.dot in a rule each time the function is called. Change line every 100 self.dots.
		Useful function for keeping the user waiting for the termination of time-consuming loops...
		
		>>> dot = self.dots()
		>>> dot.trace()
		....:....1....:....2....:....3....:....4....:....5....:....6....:....7....:....8....:....9....:....1
		....:....1....:....2....:....3....:....4....:....5....:....6....:....7....:....8....:....9....:....2
		....:....1....:....2....:....3....:....4....:....5....:.
		"""
		self.dot += 1
		if 0 > self.dot:
			pass
		elif self.dot % (100 * self.every) == 0:
			print >> sys.stderr, "\b%i\n" % (self.dot/(100*self.every)), # '\b' is there to delete the space printed by , in print 'blabla',
		elif self.dot % (10 * self.every) == 0:
			print >> sys.stderr, "\b%i" % ((self.dot/(10 * self.every)) % 10),
		elif self.dot % (5 * self.every) == 0:
			print >> sys.stderr, "\b:",
		elif self.dot % (1 * self.every) == 0:
			print >> sys.stderr, "\b.",

	def __del__(self):
		print >> sys.stderr, ''

###############################################################################

class Clock:
	"""
	Pretty print a turning bar
	"""
	
	profile = '||//--\\\\'
	modulus = 8

	def __init__(self):
		self.time = 0

	def trace(self):
		self.time = (self.time + 1) % self.modulus
		print >> sys.stderr, '\r%s' % self.profile[self.time],

	def __del__(self):
		print >> sys.stderr, '\r',

###############################################################################

def _test():
	import doctest
	doctest.testmod()
	sys.exit(0)

