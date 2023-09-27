#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from nlg.Vector import Vectors
from nlg.Cluster import ListOfClusters
from nlg.nlgCluster.StrCluster import ListOfStrClusters
from nlg.Grid import ListOfGrids

###############################################################################

__author__ = 'Fam Rashel <fam.rashel@fuji.waseda.jp>'

__date__, __version__ = '20/12/2021', '1.0' # Creation

__description__ = """Functions which provide easy interface for pipeline process to:
					- construct vector representation,
					- extract analogical clusters,
					- construct analogical grids"""

__verbose__ = False
__trace__ = False

# vectors
__char_feature__ = True

__token_feature__ = False
__token_delimiter__ = ' '

__sigmorphon__ = False
__morph_feature__ = False
__morph_delimiter__ = ';'
__lemma_feature__ = False
__lemma_dim__ = True

# clusters
__min_clu_size__ = 2
__max_clu_size__ = None
__focus__ = None

# grids
__saturation_threshold = float(0.0)
###############################################################################
# Core pipelines:
#	- strings2vectors
#	- vectors2clusters
#	- clusters2grids

def strings2vectors(lines,
					sigmorphon=__sigmorphon__,
					char_feature=__char_feature__,
					token_feature=__token_feature__, token_delimiter=__token_delimiter__,
					morph_feature=__morph_feature__, morph_delimiter=__morph_delimiter__,
					lemma_feature=__lemma_feature__, lemma_dim=__lemma_dim__,
					verbose=__verbose__):
	if verbose:
		print('\n# Building vector with feature...', file=sys.stderr)
		print(f"#\t- char : {char_feature}", file=sys.stderr)
		print(f"#\t- token: {token_feature}", file=sys.stderr)
		print(f"#\t- morph: {morph_feature}", file=sys.stderr)
		print(f"#\t- lemma: {lemma_feature}", file=sys.stderr)
	if sigmorphon:
		vectors = Vectors.fromSigmorphonFile(lines,
				char_feature=char_feature,
				morph_feature=morph_feature,
				morph_delimiter=morph_delimiter,
				lemma_feature=lemma_feature,
				lemma_dim=lemma_dim)
	else:
		vectors = Vectors.fromFile(lines,
				char_feature=char_feature,
				token_feature=token_feature,
				token_delimiter=token_delimiter)
	return vectors

def vectors2clusters(vectors,
						min_cluster_size=__min_clu_size__, max_cluster_size=__max_clu_size__, focus=__focus__,
						verbose=__verbose__):
	distinguishable_vectors = vectors.get_distinguishables()
	if verbose:
		print('# Clustering the words according to their feature vectors...', file=sys.stderr)
		print(f'#\t- min cluster size: {min_cluster_size}', file=sys.stderr)
		print(f'#\t- max cluster size: {max_cluster_size}', file=sys.stderr)
	list_of_clusters = ListOfClusters.fromVectors(distinguishable_vectors,
			minimal_size=min_cluster_size,
			maximal_size=max_cluster_size,
			focus=focus)
	if verbose: print('# Adding the indistinguishables...', file=sys.stderr)
	list_of_clusters.set_indistinguishables(vectors.indistinguishables)
	if verbose: print('# Checking distance constraints...', file=sys.stderr)
	list_of_strclusters = ListOfStrClusters.fromListOfClusters(clusters=list_of_clusters,
			minimal_size=min_cluster_size,
			maximal_size=max_cluster_size)
	return list_of_strclusters

def clusters2grids(clusters, min_cluster_size=__min_clu_size__, saturation=__saturation_threshold, verbose=__verbose__):
	if verbose:
		print('# Building grids...', file=sys.stderr)
		print(f'#\t- saturation ≥ {saturation:.3f}', file=sys.stderr)
		print(f'#\t- cluster size ≥ {min_cluster_size}', file=sys.stderr)
	list_of_grids = ListOfGrids.fromClusters(clusters, saturation)
	return list_of_grids

###############################################################################
# Additional pipeline: from lines and vectors
# 	- strings2clusters
# 	- strings2grids
#	- vectors2grids

def strings2clusters(lines,
					sigmorphon=__sigmorphon__,
					char_feature=__char_feature__,
					token_feature=__token_feature__, token_delimiter=__token_delimiter__,
					morph_feature=__morph_feature__, morph_delimiter=__morph_delimiter__,
					lemma_feature=__lemma_feature__, lemma_dim=__lemma_dim__,
					min_cluster_size=__min_clu_size__, max_cluster_size=__max_clu_size__, focus=__focus__,
					verbose=__verbose__):
	vectors = strings2vectors(lines,
			sigmorphon=sigmorphon,
			char_feature=char_feature,
			token_feature=token_feature, token_delimiter=token_delimiter,
			morph_feature=morph_feature, morph_delimiter=morph_delimiter,
			lemma_feature=lemma_feature, lemma_dim=lemma_dim,
			verbose=verbose)
	list_of_strclusters = vectors2clusters(vectors,
			min_cluster_size=min_cluster_size, max_cluster_size=max_cluster_size, focus=focus,
			verbose=verbose)
	return list_of_strclusters

def strings2grids(lines,
				sigmorphon=__sigmorphon__,
				char_feature=__char_feature__,
				token_feature=__token_feature__, token_delimiter=__token_delimiter__,
				morph_feature=__morph_feature__, morph_delimiter=__morph_delimiter__,
				lemma_feature=__lemma_feature__, lemma_dim=__lemma_dim__,
				min_cluster_size=__min_clu_size__, max_cluster_size=__max_clu_size__, focus=__focus__,
				saturation=__saturation_threshold,
				verbose=__verbose__):
	vectors = strings2vectors(lines,
			sigmorphon=sigmorphon,
			char_feature=char_feature,
			token_feature=token_feature, token_delimiter=token_delimiter,
			morph_feature=morph_feature, morph_delimiter=morph_delimiter,
			lemma_feature=lemma_feature, lemma_dim=lemma_dim,
			verbose=verbose)
	list_of_grids = vectors2grids(vectors,
			min_cluster_size=min_cluster_size, max_cluster_size=max_cluster_size, focus=focus,
			saturation=saturation,
			verbose=verbose)
	return list_of_grids

def vectors2grids(vectors,
					min_cluster_size=__min_clu_size__, max_cluster_size=__max_clu_size__, focus=__focus__,
					saturation=__saturation_threshold, verbose=__verbose__):
	list_of_strclusters = vectors2clusters(vectors,
			min_cluster_size=min_cluster_size, max_cluster_size=max_cluster_size, focus=focus,
			verbose=verbose)
	list_of_grids = clusters2grids(list_of_strclusters,
			min_cluster_size=min_cluster_size, saturation=saturation,
			verbose=verbose)
	return list_of_grids

###############################################################################
# Additional pipeline: from words (only use character feature)
# 	- words2vectors
# 	- words2clusters
#	- words2grids

def words2vectors(words, verbose=__verbose__):
	vectors = strings2vectors(words,
			char_feature=True,
			verbose=verbose)
	return vectors

def words2clusters(words,
					min_cluster_size=__min_clu_size__, max_cluster_size=__max_clu_size__, focus=__focus__,
					verbose=__verbose__):
	list_of_strclusters = strings2clusters(words,
			char_feature=True,
			min_cluster_size=min_cluster_size,
			max_cluster_size=max_cluster_size,
			focus=focus,
			verbose=verbose)
	return list_of_strclusters

def words2grids(words,
				min_cluster_size=__min_clu_size__, max_cluster_size=__max_clu_size__, focus=__focus__,
				saturation=__saturation_threshold,
				verbose=__verbose__):
	list_of_grids = strings2grids(words,
			char_feature=True,
			min_cluster_size=min_cluster_size,
			max_cluster_size=max_cluster_size,
			focus=focus,
			saturation=saturation,
			verbose=verbose)
	return list_of_grids

###############################################################################
# Additional pipeline: from sigmorphon format file (several features available)
# 	- sigmorphon2vectors
# 	- sigmorphon2clusters
#	- sigmorphon2grids

