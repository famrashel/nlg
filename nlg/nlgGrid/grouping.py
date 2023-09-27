#!/usr/bin/python3
# -*- coding: utf-8 -*-

from collections import defaultdict
###############################################################################

def clus2bins(data):
	bins = list(range(len(data)))  # Initialize each bin[n] == n
	pointer = {}
	group = [ [clu] for clu in data ]

	data = [m for m in data]  # Convert to sets
	for r, row in enumerate(data):
		for ratio in row:
			for string in ratio:
				if string not in pointer:
					# New number: tag it with a pointer to this row's bin
					pointer[string] = r
					continue
				else:
					dest = locatebin(bins, pointer[string])
					if dest == r:
						continue  # already in the same bin

					if dest > r:
						dest, r = r, dest  # always merge into the smallest bin

					group[dest].extend(group[r])
					
					group[r] = None
					# Update our indices to reflect the move
					bins[r] = dest
					r = dest

	# Filter out the empty bins
	have = [m for m in group if m]
	return have

def locatebin(bins, n):
	while bins[n] != n:
		n = bins[n]
	return n