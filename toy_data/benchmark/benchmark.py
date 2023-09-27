#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time
import argparse

import nlg.pipeline as pipeline

from tabulate import tabulate

###############################################################################

__author__ = 'Fam Rashel <fam.rashel@fuji.waseda.jp>'
__date__, __version__ = '03/10/2021', '0.10' # Creation
__description__ = 'benchmarking the nlg package'

__list_of_file__ = [
	# "../id.small.words"
	"de.words.1k",
	"fi.words.1k",
	"sv.words.1k",
	"de.words.5k",
	"fi.words.5k",
	"sv.words.5k",
	# "de.words.10k",
	# "fi.words.10k",
	# "sv.words.10k",
	# "de.words.20k",
	# "fi.words.20k",
	# "sv.words.20k"
]
###############################################################################

def read_argv():
	this_version = 'v%s (c) %s %s' % (__version__, __date__.split('/')[2], __author__)
	this_description = __description__
	this_usage = """
	%(prog)s  <  FILE_OF_WORDS
	"""

	parser = argparse.ArgumentParser(description=this_description, usage=this_usage)
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
	parser.add_argument('-V', '--verbose',
                  action='store_true', dest='verbose', default=False,
                  help='runs in verbose mode')
						
	return parser.parse_args()

def convert_time(duration):
	"""
	Convert time data (s) to human-friendly format
	"""
	m, s = divmod(round(duration), 60)
	h, m = divmod(m, 60)
	hms = "%d:%02d:%02d" % (h, m,s)
	return hms

###############################################################################

if __name__ == '__main__':
	options = read_argv()
	if options.verbose: print('# Benchmarking...', file=sys.stderr)

	time_result = []
	for i, filename in enumerate(__list_of_file__):
		result = []
		result.append(filename)

		if options.verbose: print('# Timing vector construction...', file=sys.stderr)
		t_start_1 = time.time()
		vectors = pipeline.words2vectors(open(filename), verbose=options.verbose)
		duration = time.time() - t_start_1
		result.append(duration)
		print(f'## Processing time: {(convert_time(duration))} ({duration}s)', file=sys.stderr)

		if options.verbose: print('# Timing nlg clustering...', file=sys.stderr)
		t_start = time.time()
		list_of_clusters = pipeline.vectors2clusters(vectors,
				min_cluster_size=options.minimal_cluster_size,
				max_cluster_size=options.maximal_cluster_size,
				verbose=options.verbose)
		duration = time.time() - t_start
		result.append(duration)
		print(f'## Processing time: {(convert_time(duration))} ({duration}s)', file=sys.stderr)

		if options.verbose: print('# Timing grid construction...', file=sys.stderr)
		t_start = time.time()
		list_of_grids = pipeline.clusters2grids(list_of_clusters,
				saturation=options.saturation,
				verbose=options.verbose)
		t_end = time.time()
		duration = t_end - t_start
		result.append(duration)
		print(f'## Processing time: {(convert_time(duration))} ({duration}s)', file=sys.stderr)

		result.append(t_end - t_start_1)

		time_result.append(result)
	
	print(tabulate(time_result, headers=["Filename", "Vector", "Cluster", "Grid", "Total"]), file=sys.stderr)

	if options.verbose: print(f'# {os.path.basename(__file__)} - Processing time: {(convert_time(time.time() - t_start))}', file=sys.stderr)
