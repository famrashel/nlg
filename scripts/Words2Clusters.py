#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

from datetime import datetime
from argparse import ArgumentParser

from nlg.pipeline import words2clusters

###############################################################################

__author__ = 'Yves Lepage <yves.lepage@waseda.jp>'
__date__, __version__ = '22/08/2017', '0.10' # Creation
__description__ = """
	Create clusters from a list of words (or sequence of words).
	CAUTION: each word should appear only once in the list.
"""

###############################################################################

def read_argv():
	this_version = 'v%s (c) %s %s' % (__version__, __date__.split('/')[2], __author__)
	this_description = __description__
	this_usage = '''%(prog)s  <  FILE_OF_WORDS
	'''

	parser = ArgumentParser(description=this_description, usage=this_usage, epilog=this_version)
	parser.add_argument('-F','--focus',
					action='store', type=str, default=None,
					help = 'only output those clusters which contain the word FOCUS')
	parser.add_argument('-m','--minimal_cluster_size',
					action='store', type=int, default=2,
					help = 'minimal size in clusters (default: %(default)s, ' \
								'as 1 analogy implies at least 2 ratios in a cluster)')
	parser.add_argument('-M','--maximal_cluster_size',
					action='store', type=int, default=None,
					help = 'maximal size of clusters output (default: no limit)')
	parser.add_argument('-V', '--verbose',
					action='store_true', default=False,
					help='runs in verbose mode')
	return parser.parse_args()

###############################################################################

if __name__ == '__main__':
	options = read_argv()
	t_start = datetime.now()
	if options.verbose: print('# Reading words and computing feature vectors (features=characters)...', file=sys.stderr)
	list_of_clusters = words2clusters(sys.stdin,
			min_cluster_size=options.minimal_cluster_size,
			max_cluster_size=options.maximal_cluster_size,
			focus=options.focus,
			verbose=options.verbose)
	print(list_of_clusters)
	if options.verbose: print(f'# {os.path.basename(__file__)} - Processing time: {(datetime.now() - t_start)}', file=sys.stderr)
