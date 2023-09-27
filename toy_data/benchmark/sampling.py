#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, random

sys.path.append('/Users/ylepage/ylepage/python/')
import cut 
###############################################################################

__author__ = 'Yves Lepage <yves.lepage@waseda.jp>'
__date__ = '06/08/2010'
__version__ = '1.1'
__date__ = '18/04/2012'
__version__ = '1.2'
__description__ = '''First form: output a sample of SIZE lines from the standard input (default SIZE=length of input).
Second form with option -l: outputs only those lines given as parameters in that order (no sampling here).
'''

__verbose__ = False
__sample_size__ = None
__shuffle__ = False

###############################################################################

def sampling(fin=sys.stdin, fout=sys.stdout, size=__sample_size__, shuffle=__shuffle__, line_numbers=None, percent=False):
	lines = {}
	n = 0
	for line in fin:
		lines[n] = line
		n += 1
	if percent:
		size = n * size // 100
	if line_numbers == None: # sampling
		linenumbers = range(n)
		random.shuffle(linenumbers)
		if shuffle:
			# if size is None, will work fine: will take all lines in the file
			linenumbers = linenumbers[:size]
		else:
			linenumbers = sorted(linenumbers[:size])
		for i in linenumbers:
			print >> fout, lines[i],
	else: # no sampling here, just selecting lines from a file
		for (start,end) in cut.parse_field_numbers(line_numbers):
			for i in xrange(max(1,start),min(n,end)):
				print >> fout, lines[i],

###############################################################################

def read_argv():
	from optparse import OptionParser
	this_version = 'v%s (c) %s %s' % (__version__, __date__.split('/')[2], __author__)
	this_description = __description__
	this_usage =	"""usage: %prog [-s] [SIZE]
       %prog -l LINE-NUMBERS 
	"""

	parser = OptionParser(version=this_version, description=this_description, usage=this_usage)
	parser.add_option("-s", "--shuffle",
							action="store_true", dest="shuffle", default=False,
	                  help="shuffle the lines, i.e., do not keep the order in the original file")
	parser.add_option("-p", "--percent",
							action="store_true", dest="percent", default=False,
	                  help="the size is in percent, e.g., 60 means 60 %")
	parser.add_option("-l", "--line-numbers",
                  dest="line_numbers", default=None,
                  help="""A comma-separated list of line numbers
(1-based) where runs of fields can be specified by a dash (e.g.
"3-5,1").""")
	(options, args) = parser.parse_args()	
	return options, args

###############################################################################

if __name__ == '__main__':
	try:
		import psyco
		psyco.full()
	except ImportError:
		pass
	options, args = read_argv()
	if len(args) > 0:
		__sample_size__ = int(args[0])		
	sampling(size=__sample_size__, shuffle=options.shuffle, line_numbers=options.line_numbers, percent=options.percent)
	sys.exit()
		

		
