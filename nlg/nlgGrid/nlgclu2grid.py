#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import argparse
import multiprocessing as mp

from nlg.Cluster import Cluster
from nlg.Grid import Grid
from nlg.Grid import ListOfGrids
from nlg.nlgGrid.grouping import clus2bins

###############################################################################

__author__ = 'Fam Rashel <fam.rashel@fuji.waseda.jp>'

__date__, __version__ = '01/05/2016', '1.0' # Creation
__date__, __version__ = '10/12/2021', '1.1' # Introduce multiprocessing using simple technique to group clusters into bins

__description__ = 'Build analogical grids from list of analogical clusters ' \
					'typically produced by nlgclu.py -f simplified or by strnlgclu.py.'

__verbose__ = False		# Gives information about timing, etc. to the user.
__trace__ = False		# To be used by the developper for debugging.

###############################################################################

__min_clu_size__			= 3
__saturation_threshold__	= 0
__pretty_print_file__		= None

###############################################################################

def read_clusters(file, min_clu_size=__min_clu_size__, saturation_threshold=__saturation_threshold__, verbose=__verbose__, trace=__trace__):
	""" Read and filter (by size) analogical clusters from file"""
	clusters = list()
	if verbose: print('# Reading clusters...', file=sys.stderr)
	for i, line in enumerate(file):
		clu = Cluster(line)
		if len(clu) >= min_clu_size: clusters.append(clu)
		if trace: print('### [%d] => %s' % (i, clu), file=sys.stderr)
		if verbose: print('\r# Number of analogical clusters read: %d\t' % i, end=' ', file=sys.stderr)
	if verbose:
		print('\n# Filtered analogical clusters with min size %d: %d' % (min_clu_size, len(clusters)), file=sys.stderr)
		print('# Building grids with saturation threshold ≥ %.3f...' % saturation_threshold, file=sys.stderr)
	return sorted(clusters, key=len, reverse=True)

def nlgclus2grids(clusters, saturation=__saturation_threshold__, verbose=__verbose__, trace=__trace__):
	"""
	Build list of analogical grids from list of analogical clusters.
	Clusters -> Bins -> Grids
	"""
	list_of_grids = ListOfGrids([])
	inserted_clu = 0
	gridnbr = 0
	while len(clusters) > 0:
		grid = Grid([])
		last_size = 0
		while last_size != len(clusters) and len(clusters) != 0:
			last_size = len(clusters)
			for cluster in clusters:
				if trace: print('### Trying to insert:\n### %s' % (cluster), file=sys.stderr)
				insertable, position = grid.checkninsert(cluster, saturation)
				if insertable:
					clusters.remove(cluster)
					inserted_clu += 1
				if trace: print('### %s - %s\n%s' % (insertable, position, grid.pretty_print()), file=sys.stderr)
		grid.set_attributes()
		list_of_grids.append(grid)
		gridnbr += 1
		del grid
		if verbose: print('\r## No of grids produced: %d - No of inserted clusters: %d' % (gridnbr, inserted_clu), end=' ', file=sys.stderr)

	return list_of_grids
	
###############################################################################
# Paralellised version
def clus2grids(clusters, saturation=__saturation_threshold__, verbose=__verbose__):
	"""
	Build list of analogical grids from list of analogical clusters.
	Clusters -> Bins -> Grids
	"""
	list_of_grids = ListOfGrids([])

	# group clusters into bins
	bins = clus2bins(clusters)
	if verbose:
		print('# Putting clusters into {} bin(s)...'.format(len(bins)), file=sys.stderr)

	# for i, clu_bin in enumerate(bins):
	# 	if __verbose__:
	# 		print('# Processing bin: {} with {} cluster(s)...'.format(i+1, len(clu_bin)), file=sys.stderr)
	# 	list_of_grids.extend(construct_grids(clu_bin, saturation))
	
	# multiprocessing on each bin
	if verbose:
		print('# Multiprocessing pool: {}'.format(mp.cpu_count()), file=sys.stderr)
	pool = mp.Pool(mp.cpu_count())
	result = [ pool.apply_async(construct_grids, args=(clu_bin, saturation, verbose)) for clu_bin in bins ]
	for r in result:
		list_of_grids.extend( r.get())
	pool.close()
	return list_of_grids

def construct_grids(list_of_clus, saturation=__saturation_threshold__, verbose=__verbose__, trace=__trace__):
	list_of_grids = ListOfGrids([])
	inserted_clu = 0
	gridnbr = 0
	while len(list_of_clus) > 0:
		grid = Grid([])
		last_size = 0
		while last_size != len(list_of_clus) and len(list_of_clus) != 0:
			last_size = len(list_of_clus)
			for cluster in list_of_clus:
				if trace: print('### Trying to insert:\n### %s' % (cluster), file=sys.stderr)
				insertable, position = grid.checkninsert(cluster, saturation)
				if insertable:
					list_of_clus.remove(cluster)
					inserted_clu += 1
				if trace: print('### %s - %s\n%s' % (insertable, position, grid.pretty_print()), file=sys.stderr)
		grid.set_attributes()
		list_of_grids.append(grid)
		gridnbr += 1
		del grid
		if verbose: print('\r## No of grids produced: %d - No of inserted clusters: %d' % (gridnbr, inserted_clu), end=' ', file=sys.stderr)
	if verbose:
		print("", file=sys.stderr)
	return list_of_grids

###############################################################################

def read_argv():

	this_version = 'v%s (c) %s %s' % (__version__, __date__.split('/')[2], __author__)
	this_description = __description__
	this_usage = """
	%(prog)s  <  FILE_OF_CLUSTERS
	"""

	parser = argparse.ArgumentParser(version=this_version, description=this_description, usage=this_usage)
	parser.add_argument('-s', '--clu-size',
                  action='store', dest='cluster_size', type=int, default=3,
                  help='min cluster size to use when building grids (default = %(default)s)')
	parser.add_argument('-d', '--saturation',
                  action='store', dest='saturation', type=float, default=0,
                  help='min saturation (0 - 1.0) to keep when building grids (default = %(default)s)')
	parser.add_argument('-p', '--pretty-print',
                  action='store', dest='pretty_print', type=str,
                  help='print the grids in the representation for HUMAN to the file')
	parser.add_argument('-S', '--statistics',
                  action='store_true', dest='statistics', default=False,
                  help='output statistics of the grids (not yet implemented)')
	parser.add_argument('-V', '--verbose',
                  action='store_true', dest='verbose', default=False,
                  help='runs in verbose mode')
	parser.add_argument('-t', '--trace',
                  action='store_true', dest='trace', default=False,
                  help='runs in tracing mode')
	parser.add_argument('-T', '--test',
                  action='store_true', dest='test', default=False,
                  help='run all unitary tests')
		
	return parser.parse_args()

###############################################################################

def _test():
	import doctest
	doctest.testmod()
	sys.exit(0)

def main(file=sys.stdin):
	"""
	Mainly a copy of nlgclus2grids function w/o holding the constructed grids in the memory.
	This function is way more inexpensive in memory load.
	Grid's class objects are expensive!
	(Need to work on it :p)
	"""
	clusters = read_clusters(file)		# Reading clusters

	# grids_words = Set()
	# grids_predictablewords = Set()
	gridnbr = 0
	inserted_clu = 0
	while len(clusters) > 0:
		grid = Grid([])
		last_size = 0
		while last_size != len(clusters) and len(clusters) != 0:
			last_size = len(clusters)
			for cluster in clusters:
				if __trace__: print('### Trying to insert:\n### %s' % (cluster), file=sys.stderr)
				insertable, position = grid.checkninsert(cluster, __saturation_threshold__)
				if insertable:
					clusters.remove(cluster)
					inserted_clu += 1
				if __trace__: print('### %s - %s\n%s' % (insertable, position, grid.pretty_print()), file=sys.stderr)
		grid.set_attributes()
		print(grid)
		gridnbr += 1

		if __pretty_print_file__ != None:
			__pretty_print_file__.write('# Grid no.: %d - %s\n' % (gridnbr, str(grid.attributes)))
			__pretty_print_file__.write('%s\n\n' % grid.pretty_print())

		# Get list of words in grid
		# grid._update_term_index()
		# for term in grid.term_index:
		# 	grids_words.add(term)

		# Get predictable words from grid
		# empty_cells = grid.predictable_words()
		# # print empty_cells
		# if len(empty_cells) != 0: grids_predictablewords |= empty_cells
		
		del grid	# Free the memory
		if __verbose__: print('\r## No of grids produced: %d - No of inserted clusters: %d' % (gridnbr, inserted_clu), end=' ', file=sys.stderr)
	
	# print 'List of words in the grids:'
	# print grids_words
	# print 'List of predictable words in the grids:'
	# print grids_predictablewords

if __name__ == '__main__':
	options = read_argv()
	if options.test: _test()
	if options.pretty_print: __pretty_print_file__ = open(options.pretty_print, 'w')
	__saturation_threshold__ = options.saturation
	__min_clu_size__ = options.cluster_size
	__verbose__ = options.verbose
	__trace__ = options.trace

	t1 = time.time()
	main(sys.stdin)
	if options.pretty_print: __pretty_print_file__.close()
	if __verbose__: print('\n# Processing time: ' + ('%.2f' % (time.time() - t1)) + 's', file=sys.stderr)
