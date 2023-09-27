#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

from datetime import datetime
from argparse import ArgumentParser

from nlg.Vector import Vectors
from nlg.pipeline import vectors2grids

###############################################################################

__author__ = 'Fam Rashel <fam.rashel@fuji.waseda.jp>'
__date__, __version__ = '03/09/2020', '0.10' # Creation
__description__ = 'Produce analogical grids from a list of vectors.'

###############################################################################

def read_argv():
	this_version = 'v%s (c) %s %s' % (__version__, __date__.split('/')[2], __author__)
	this_description = __description__
	this_usage = """
	%(prog)s  <  FILE_OF_VECTORS
	"""

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
	parser.add_argument('-d', '--saturation',
						action='store', dest='saturation', type=float, default=0,
						help='min saturation (0 - 1.0) to keep when building grids (default = %(default)s)')
	parser.add_argument('--pretty-print',
						action='store', dest='pretty_print', type=str, default=None,
						help='print the grids in the representation for HUMAN instead of SCRIPT format')
	parser.add_argument('-V', '--verbose',
                  action='store_true', dest='verbose', default=False,
                  help='runs in verbose mode')
						
	return parser.parse_args()

###############################################################################

if __name__ == '__main__':
	options = read_argv()
	t_start = datetime.now()
	if options.verbose: print('# Reading words and their vector representations...', file=sys.stderr)
	vectors = Vectors.fromListOfVectors(lines=sys.stdin)
	list_of_grids = vectors2grids(vectors,
			min_cluster_size=options.minimal_cluster_size,
			max_cluster_size=options.maximal_cluster_size,
			focus=options.focus,
			saturation=options.saturation,
			verbose=options.verbose)
	
	if options.pretty_print == '':
		print(list_of_grids.pretty_print())
	elif options.pretty_print is not None:
		grids_pretty_print_file = open(options.pretty_print, 'w')
		grids_pretty_print_file.write(list_of_grids.pretty_print())
		grids_pretty_print_file.close()
	else:
		print(list_of_grids)
	if options.verbose: print(f'# {os.path.basename(__file__)} - Processing time: {(datetime.now() - t_start)}', file=sys.stderr)
