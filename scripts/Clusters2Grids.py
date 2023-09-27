#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

from datetime import datetime
from argparse import ArgumentParser

from nlg.Cluster import ListOfClusters
from nlg.pipeline import clusters2grids

###############################################################################

__author__ = 'Fam Rashel <fam.rashel@fuji.waseda.jp>'
__date__, __version__ = '22/08/2017', '0.10' # Creation
__description__ = """
	Produce analogical grids from a list of clusters (or sequence of words).
"""

###############################################################################

def read_argv():
	this_version = 'v%s (c) %s %s' % (__version__, __date__.split('/')[2], __author__)
	this_description = __description__
	this_usage = """
	%(prog)s  <  FILE_OF_CLUSTERS
	"""

	parser = ArgumentParser(description=this_description, usage=this_usage, epilog=this_version)
	parser.add_argument('-c','--min_cluster_size',
					action='store', dest='minimal_grids_cluster_size' , type=int, default=2,
					help = 'min size of clusters (default: %(default)s) to use')
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
	if options.verbose: print('# Reading clusters...', file=sys.stderr)
	list_of_clusters = ListOfClusters.fromFile(sys.stdin)
	# print list_of_strclusters								# Print clusters
	list_of_grids = clusters2grids(list_of_clusters,
			min_cluster_size=options.minimal_grids_cluster_size,
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
