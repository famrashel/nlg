#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import doctest
import time
import collections
import itertools
import math
import copy

from tabulate import tabulate

# from dots import Dots
from _fast_distance import fast_similitude
from scipy.optimize import linear_sum_assignment

###############################################################################

__author__ = 'Yves Lepage <yves.lepage@waseda.jp>'
__date__, __version__ = '31/03/2017', '1.0'	# Creation
__date__, __version__ = '03/04/2017', '1.1'	# Corrected bug in formula for matching points.
__date__, __version__ = '03/04/2017', '1.2'	# Convert to Python3 (FR)
__description__ = 'Yet another analogy solver based on character-position arithmetic.'

__verbose__ = False
__trace__ = False

__nlg_fmt__ = u'%s : %s :: %s : %s'

class Option:
	pass

options = Option()
options.virtual_markers				= True
options.diagonal_band				= True
options.expectation_maximisation	= True
options.hungarian_method			= True

###############################################################################

def padding(terms):
	maxlen = max(len(term) for term in terms)
	return [ '<' * (maxlen - len(term)) + term for term in terms ]

def slicing(terms):
	maxlen = max(len(term) for term in terms)
	return [ '*'.join(list(term)) for term in terms ]

###############################################################################

def entropy(list):
	s = float(sum(list))
	if s == 0.0:
		# For p = 0.0, we assign 0.0 to - p log p,
		# because \lim_{p \rightarrow 0} p \times \log p = 0.0.
		return 0.0
	else:
		if __trace__: print >> sys.stderr, [ prob for prob in [ x/s for x in list ] ]
		return -1.0 * sum( prob * math.log(prob, 2) if prob > 0.0 else 0.0 for prob in [ x/s for x in list ] )

###############################################################################

def contains(counter1, counter2):
	if False: print >> sys.stderr, '%s <? %s)' % (counter1, counter2)
	for c in counter2:
		if c not in counter1:
			return False
	for c in counter1:
		if counter1[c] < counter2[c]:
			return False
	return True

###############################################################################

class Analogy:

	def __init__(self, A, B, C):
		if __verbose__: print >> sys.stderr, ('in  Initialise(' + __nlg_fmt__ + ')') % (A, B, C, "x")
		# Remember the terms of the analogical equation.
		self.A, self.B, self.C = A, B, C
		D = self.D = None
		# Compute the lengths of all the terms.
		self.len = { X: len(X) for X in (A, B, C) }
		self.len[D] = len(B) + len(C) - len(A)
		if __verbose__: print >> sys.stderr, '# lenA = %d, lenB = %d, lenC = %d, lenD = %d' % tuple( self.len[X] for X in (A, B, C, D) )
		# Compute the multisets for all the terms.
		self.m = { X: collections.Counter(X) for X in (A, B, C) }
		self.m[D] = self.m[B] + self.m[C] - self.m[A]
		self.DD = ''.join( cD * self.m[D][cD] for cD in sorted(self.m[D]) )
		self.has_zero_solution = self.zero_solution()
		if __verbose__: print >> sys.stderr, ('No solution for ' + __nlg_fmt__) % (A, B, C, "x")
		if __trace__: print >> sys.stderr, '# mA = %s, mB = %s, mC = %s, mD = %s' % tuple( self.m[X] for X in (A, B, C, D) )
		# Compute the similarities between all the terms of the analogical equation.
		self.s = {}
		# self.s[A] = { X: fast_similitude(self.A.encode('utf8'), X.encode('utf8')) for X in (self.B, self.C) }	# RF-Commented due to encode bug
		self.s[A] = { X: fast_similitude(self.A, X) for X in (self.B, self.C) }
		self.s[D] = { B: self.s[A][C] - self.len[A] + self.len[B], C: self.s[A][B] - self.len[A] + self.len[C] }
		if B not in self.s: self.s[B] = {}
		self.s[B][A], self.s[B][D] = self.s[A][B], self.s[D][B]
		if C not in self.s: self.s[C] = {}
		self.s[C][A], self.s[C][D] = self.s[A][C], self.s[D][C]
		if __verbose__: print >> sys.stderr, '# s[X][Y] =\n\tB\tC\nA\t%d\t%d\nD\t%d\t%d' % tuple( self.s[X][Y] for X in (A, D) for Y in (B, C) )
		if __verbose__: print >> sys.stderr, ('out Initialise(' + __nlg_fmt__ + ')') % (A, B, C, "x")
	
	def zero_solution(self):
		return self.len[self.D] < 0 or any( 0 > - self.A.count(cD) + self.B.count(cD) + self.C.count(cD) \
											for cD in set(self.A) | set(self.B) | set(self.C) )
	
	def InsideBand(self, X, Y, iX, iY, names=['A', 'B']):
		if __trace__: print >> sys.stderr, '# in  InsideBand(%s=%s, %s=%s, i%s=%d, i%s=%d)' % (names[0], X, names[1], Y, names[0], iX, names[1], iY)
		if __trace__: print >> sys.stderr, '# - len[%s]=%d + s[%s][%s]=%d <= i[%s]=%d - i[%s]=%d <= len[%s]=%d - s[%s][%s]=%d' % \
						(names[0], self.len[X], names[0], names[1], self.s[X][Y], names[1], iY, names[0], iX, names[1], self.len[Y], names[0], names[1], self.s[X][Y])
		result = - self.len[X] + self.s[X][Y] <= iY - iX <= self.len[Y] - self.s[X][Y]
		if __trace__: print >> sys.stderr, '# out InsideBand(X=%s, Y=%s, iX=%d, iY=%d) = %s' % (X, Y, iX, iY, result)
		return result

	def InsideAllBands(self, A, B, C, iA, iB, iC, names=['A', 'B', 'C', 'D']):
		i = { A: iA, B: iB, C: iC, self.D: iB + iC - iA }
		return all( self.InsideBand(X, Y, i[X], i[Y], names=Z) for (X, Y, Z) in ((A, C, ['A', 'C']), (B, self.D, ['B', 'D']), (C, self.D, ['C', 'D'])) )

	def AllEvidences(self, A, B, C, names=['A', 'B', 'C']):
		if __verbose__: print >> sys.stderr, '# AllEvidences(%s, %s, %s)' % (A, B, C)
		if options.virtual_markers:
			if __trace__: print >> sys.stderr, 'Use vitual markers.'
			for iB in range(self.len[B]):
				for iD in ( iB, iB + self.len[C] - self.len[A] ):
					if 0 <= iD < self.len[self.D]:
						self.M[B[iB]][iD] += 1
			for iC in range(self.len[C]):
				for iD in ( iC, iC + self.len[B] - self.len[A] ):
					if 0 <= iD < self.len[self.D]:
						self.M[C[iC]][iD] += 1
		else:
			if __trace__: print >> sys.stderr, 'DO NOT use vitual markers.'
		for iA in range(self.len[A]):
			for iB in range(self.len[B]):
				for iC in range(self.len[C]):
					iD = iB + iC - iA
					if 0 <= iD < self.len[self.D]:
						self.M[A[iA]][iD] -= 1
						self.M[B[iB]][iD] += 1
						self.M[C[iC]][iD] += 1
		# Avoid negative evidence => Subtract min to all cells if negative min.
		minval = min( self.M[cD][iD] for cD in self.M for iD in self.M[cD] )
		if minval < 0:
			for cD in self.M:
				for iD in self.M[cD]:
					self.M[cD][iD] -= minval

	def Evidence(self, A, B, C, names=['A', 'B', 'C']):
	
		def pr(A, iA):
			if iA < 0:			return '>'
			elif iA >= len(A):	return '<'
			else:				return A[iA]
	
		def MakeEvidence(self, A, B, C, iA, iB, names=['A', 'B', 'C']):
			if __trace__: print >> sys.stderr, 'A = %s, B = %s, C = %s, iA = %d, iB = %d' % (A, B, C, iA, iB)
			for iC in range(self.len[C]):
				iD = iB + iC - iA
#				if C[iC] in self.m[self.D].keys() and self.InsideBand(C, self.D, iC, iD, names=[names[2], 'D']):
				if C[iC] in self.m[self.D].keys() and self.InsideAllBands(A, B, C, iA, iB, iC, names=names+['D']):
					if 0 <= iD < self.len[self.D]:
						if __trace__: print >> sys.stderr, '# %s[%d] = %c = %s[%d]  =>  %s[%d] = %c = D[%d]' % \
									(names[0], iA, pr(A,iA), names[1], iB, names[2], iC, pr(C,iC), iD)
						self.M[C[iC]][iD] += 1
	
		if __verbose__: print >> sys.stderr, '# Evidence(%s, %s, %s)' % (A, B, C)
		if options.virtual_markers:
			if __trace__: print >> sys.stderr, 'Use virtual beginning markers.'
			MakeEvidence(self, A, B, C,     -1,     -1, names)
		else:
			if __trace__: print >> sys.stderr, 'DO NOT use virtual markers.'
		for (iA, iB) in itertools.product(range(self.len[A]), range(self.len[B])):
			if A[iA] == B[iB] and self.InsideBand(A, B, iA, iB, names=[names[0], names[1]]):
				# if __trace__: print >> sys.stderr, '# %s[%d] = %c = %s[%d]' % (names[0], iA, A[iA].encode('utf8'), names[1], iB)	# RF-Commented due to encode bug
				if __trace__: print >> sys.stderr, '# %s[%d] = %c = %s[%d]' % (names[0], iA, A[iA], names[1], iB)
				MakeEvidence(self, A, B, C, iA, iB, names)
		if options.virtual_markers:
			if __trace__: print >> sys.stderr, 'Use vitual end       markers.'
			MakeEvidence(self, A, B, C, len(A), len(B), names)
#		for cD in self.M:
#			for iD in self.M[cD]:
#				self.M[cD][iD] += 1

	def Enumerate(self, allchar, iD=0, lenD=None, solution=None):
		"""
		Enumerate all the solutions
		by trying each character for all possible postions.
		Filter out solutions for which the mulitset is wrong.
		"""
		if __trace__: print >> sys.stderr, '# in  Enumerate(%s, iD=%d, lenD=%d)...' % (allchar, iD, lenD if lenD != None else -1)
		if __trace__: print >> sys.stderr, '# self.m[D] = %s' % self.m[self.D]
		if iD == 0:
			lenD = self.len[self.D]
		if iD < lenD:
			if solution != None:
				solhead, soltail = set([solution[0]]), solution[1:] if len(solution) > 0 else ''
			else:
				solhead, soltail = set([]), None
			heads, tails = set(allchar[iD]), self.Enumerate(allchar, iD+1, lenD=lenD, solution=soltail)
			if not solhead <= heads:
				return set([''])
			elif solution != None:
				heads = solhead
			results = set( head+tail for head in heads for tail in tails )
			results = set( result for result in results if contains(self.m[self.D], collections.Counter(result)) )
			if __trace__: print >> sys.stderr, '# mid Enumerate results = %s' % results
			if iD == 0:
				results = set( s for s in results if ''.join(cD * s.count(cD) for cD in sorted(set(s))) == self.DD )
				results = set( s for s in results if len(s) == self.len[self.D] )
			if __trace__: print >> sys.stderr, results
		elif iD >= lenD:
			results = set([''])
		if __trace__: print >> sys.stderr, '# out Enumerate(%s, iD=%d, lenD=%d) = %s' % (allchar, iD, lenD if lenD != None else -1, results)
		return results

	def SolutionSet(self, MM, lin, col, solution=None):
		if __verbose__: print >> sys.stderr, '# in  SolutionSet(lin=%s, col=%s)...' % (lin, col)
		# For each character, list all positions with same value as
		# in solution given by (lin, col).
		allpos = { ic: [ jD for jD in range(len(MM)) if MM[ic][jD] == MM[ic][iD] ] for (ic, iD) in zip(lin, col) }
		if __trace__: print >> sys.stderr, 'allpos  = %s' % allpos
		# For each position, list each possible character.
		allchar = collections.defaultdict(list)
		for ic in allpos:
			for iD in allpos[ic]:
				allchar[iD].append(self.DD[ic])
		allchar = { iD: set(allchar[iD]) for iD in allchar }
		if __trace__: print >> sys.stderr, 'allchar = %s' % allchar
		# Enumerate all solutions by trying each possible character for each position.
		# Check whether the solution is valid.
		if sorted(allchar.keys()) != range(self.len[self.D]):
			result = set()
		else:
			result = self.Enumerate(allchar, solution=solution)
		if __trace__: print >> sys.stderr, 'solution = %s' % result
		if __verbose__: print >> sys.stderr, '# out SolutionSet(lin=%s, col=%s) = %s' % (lin, col, result)
		return result

	def IncreasingEntropies(self, MM):
		"""
		Output a string which corresponds to the description given by MM:
			score for each character at each position.
		Dividing by the sum of scores for one character,
			this gives the probability for that character to be at a given position.
		The character with the least entropy is the one for which there is less ambiguity to choose between several positions.
		The entropy is maximal when the probability distribuion is equiprobable:
			we cannot decide on a position,
				because all are as good.
		We examine the characters with the least entropy in turn.
		Each time we decide for a character at a given position,
			we decrease the number of times the character may appear in the solution and
			delete that position.
		"""
		if __verbose__: print >> sys.stderr, '# in  IncreasingEntropies()...'
		if __trace__: print >> sys.stderr, '# mid IncreasingEntropies: \n%s' % MM
		if __trace__: print >> sys.stderr, '%s' % self.visualize(MM)
		multisetDD = copy.deepcopy(self.m[self.D])
#		listD = [ '.' ] * self.len[self.D]
		lincol = []
		MMcopy = copy.deepcopy(MM)
		while sum(multisetDD.values()) != 0:
			if __trace__: print >> sys.stderr, '*** Loop:\n%s' % MMcopy
			row_entropies = { cD: entropy(MMcopy[ic]) for ic, cD in enumerate(multisetDD) if multisetDD[cD] != 0 }
			if __trace__: print >> sys.stderr, 'row entropies = %s' % row_entropies
			cD = min(row_entropies, key=row_entropies.get)
			# Remember the minimal entropy and
			# loop over all characters with this value of entropy.
			minD = row_entropies[cD]
			list_min_entropy_cD = [ cD for cD in row_entropies if row_entropies[cD] == minD ]
			for cD in list_min_entropy_cD:
				# Choose the last position of character cD in self.DD.
				# The number of occurrences of character cD which remain in self.DD is multisetDD[cD].
				ic = self.DD.index(cD)+multisetDD[cD]-1
				if __trace__: print >> sys.stderr, 'self[%c] = %s' % (cD, MMcopy[ic])
				vD = dict(enumerate(MMcopy[ic]))
				# Select the position with the maximal value.
				# Insert the character at this position in the solution.
				iD = max(vD, key=vD.get)
				if __trace__: print >> sys.stderr, 'D[%d] = %c' % (iD, cD)
#				listD[iD] = cD
				# Decrement the number of occurrences of character cD which remain in self.DD.
				multisetDD[cD] -= 1
				if __trace__: print >> sys.stderr, 'iD, index in self.DD = (%d, %d)' % (iD, self.DD.index(cD)+multisetDD[cD]-1)
				lincol.append((ic, iD))
				if __trace__: print >> sys.stderr, 'ic, iD = (%d, %d)' % (ic, iD)
				for ic in range(len(MMcopy)):
					MMcopy[ic][iD] = 0
#		return set([''.join(listD)])
		lin, col = zip(*lincol)
		if __verbose__: print >> sys.stderr, '# out IncreasingEntropies() = lin=%s, col=%s' % (lin, col)
		return lin, col

	def HungarianMethod(self, MM):
		if __verbose__: print >> sys.stderr, '# in  HungarianMethod()...'
		# We need to subtract each value to the max value
		# because the function called (linear_sum_assignment) solves a minumal cost assignment problem.
		maxval = max( max(line) for line in MM )
		oppMM = [ [ maxval - cell for cell in line ] for line in MM ]
		lin, col = linear_sum_assignment(oppMM)
		lin, col = list(lin), list(col)
		if __verbose__: print >> sys.stderr, '# out HungarianMethod() = lin=%s, col=%s' % (lin, col)
		return lin, col

	def ExpectationMaximisation(self, MM):
		# t(f|e) is computed from the matrix M
		# f is character cD, e is the position iD
		if __verbose__: print >> sys.stderr, 'in  ExpectationMaximisation()'
		lenD = self.len[self.D]
		sums = [ float(sum( MM[cD][iD] for cD in range(lenD) )) for iD in range(lenD) ]
		for cD in range(lenD):
			for iD in range(lenD):
				MM[cD][iD] /= sums[iD] if sums[iD] != 0.0 else 1.0
		__epsilon__, steps = 1.00 / (lenD**2), 0
		while True:
			steps += 1
			count = { cD: { iD: 0.0 for iD in range(lenD) } for cD in range(lenD) }
			total = { iD: 0 for iD in range(lenD) }
			for cD in range(lenD):
				total_s = 0.0
				for iD in range(lenD):
					total_s += MM[cD][iD]
				for iD in range(lenD):
					count[cD][iD] += MM[cD][iD] / total_s if total_s != 0.0 else 0.0
					total[iD]	  += MM[cD][iD] / total_s if total_s != 0.0 else 0.0
			delta = 0.0
			for iD in total:
				for cD in [ cD for cD in count if count[cD][iD] != 0.0 ]:
					previous = MM[cD][iD]
					MM[cD][iD] = count[cD][iD] / total[iD] if total[iD] != 0.0 else 0.0
					delta = max(delta, abs(MM[cD][iD] - previous))
			# Exit condition.
			if delta < __epsilon__: break
		if __verbose__: print >> sys.stderr, 'mid ExpectationMaximisation() converged in %d steps' % steps
		if __verbose__: print >> sys.stderr, 'out ExpectationMaximisation()'
		return MM

	def Solve(self, unique=False, solution=None):
		if self.len[self.D] == 0: return set([''])
		if self.has_zero_solution: return set()
		if __verbose__: print >> sys.stderr, ('in  Solve(' + __nlg_fmt__ + ')')  % (self.A, self.B, self.C, "x")
		if not options.diagonal_band:
			# Compute the matrix position x character by character-position
			# arithmetic for all positions.
			allchars = set(self.A+self.B+self.C)
			self.M = { c: { i: 0 for i in range(self.len[self.D]) } for c in allchars }
			self.AllEvidences(self.A, self.B, self.C, names=['A', 'B', 'C'])
		else:
			# 1. Initialise the matrix position x character.
			self.M = { c: { i: 0 for i in range(self.len[self.D]) } for c in self.m[self.D].keys() }
			# 2.a. Accumulate evidence for characters and positions in solutions.
			self.Evidence(self.A, self.B, self.C, names=['A', 'B', 'C'])
			# 2.a. Do same thing as above by exchanging B and C.
			self.Evidence(self.A, self.C, self.B, names=['A', 'C', 'B'])
		# Prepare the matrix for the assignment problem.
		MM = [ [ self.M[cD][iD] for iD in range(self.len[self.D]) ] for cD in self.DD ]
		if __verbose__: print >> sys.stderr, '%s' % self.visualize(MM, solution)
		if options.expectation_maximisation:
			MM = self.ExpectationMaximisation(MM)
			MM = [ [ int(round(MM[i][j] * self.len[self.D] * 10)) for j in range(len(MM[i])) ] for i in range(len(MM)) ]
#		else:
#			MM = [ [ 0 if MM[i][j] == 0 else 1 for j in xrange(len(MM[i])) ] for i in xrange(len(MM)) ]
		# Visualise the matrix position x character.
		if __verbose__: print >> sys.stderr, '%s' % self.visualize(MM, solution)
		# 3. Interpret M as an optimal assignment problem and solve it.
		if options.hungarian_method:
			lin, col = self.HungarianMethod(MM)
		else:
			lin, col = self.IncreasingEntropies(MM)
		if __verbose__: print >> sys.stderr, '%s' % self.visualize(MM)
		# Output plurality of solutions if asked for.
		if unique:
			s = { iD: self.DD[ic] for (ic, iD) in zip(lin, col) }
			if __verbose__: print >> sys.stderr, 's = %s' % s
			self.D = set([''.join(s[iD] for iD in sorted(s.keys()))])
		else:
			self.D = self.SolutionSet(MM, lin, col, solution=None)
		if __verbose__: print >> sys.stderr, ('out Solve(' + __nlg_fmt__ + ')')  % (self.A, self.B, self.C, self.D)
		return self.D

	def AllSolve(self, solution):
		if __verbose__: print >> sys.stderr, ('in  Solve(' + __nlg_fmt__ + ')')  % (self.A, self.B, self.C, "x")
		# 1. Initialise the matrix position x character.
		allchars = set(self.A+self.B+self.C)
		self.M = { c: { i: 0 for i in range(self.len[self.D]) } for c in allchars }
		# 2.a. Accumulate evidence for characters and positions in solutions.
		self.AllEvidences(self.A, self.B, self.C, names=['A', 'B', 'C'])
		# 3. Interpret M as an optimal assignment problem.
		MM = [ [ self.M[cD][iD] for iD in range(self.len[self.D]) ] for cD in solution ]
		# Visualise the matrix position x character.
		if __verbose__: print >> sys.stderr, '%s' % self.visualize(MM, solution)
		# We need to subtract each value to the max value
		# because the function called solves the minumum assignment problem.
#		maxval = max( max(line) for line in MM )
#		MM = [ [ maxval - cell for cell in line ] for line in MM ]
		lin, col = self.HungarianMethod(MM)
		s = { iD: self.DD[ic] for (ic, iD) in zip(lin, col) }
		self.D = set([''.join( s[iD] for iD in sorted(s.keys()) )])
		if __verbose__: print >> sys.stderr, ('out Solve(' + __nlg_fmt__ + ')')  % (self.A, self.B, self.C, self.D)
		return self.D

	def visualize(self, MM, solution=None):
		if solution != None:
			table = { c: MM[i] for i, c in enumerate(self.DD) }
			table = [ [ c ] + table[c] for c in solution ]
			headers = [' '] + [ c for c in solution ]
		else:
			table = [ [ c ] + MM[i] for i, c in enumerate(self.DD) ]
			headers = 'keys'
		s = ''
		if len(table) != 0:
			s += tabulate(table, headers=headers).replace(' 0', ' .')
			s += '\n'
		return s

###############################################################################

def read_argv():

	from optparse import OptionParser
	this_version = 'v%s (c) %s %s' % (__version__, __date__.split('/')[2], __author__)
	this_description = __description__
	this_usage = '''%prog [-h N]  <  benchmark_[true|false].txt
	'''

	parser = OptionParser(version=this_version, description=this_description, usage=this_usage)
	parser.add_option('--virtual',
                  action='store_false', dest='virtual_markers', default=True,
                  help='do not add virtual beginning and end markers ' \
				  		'(default: add them)')
	parser.add_option('--DB',
                  action='store_false', dest='diagonal_band', default=True,
                  help='do not use the diagonal band constraint ' \
				  		'(default: consider character-position arithmetic only inside diagonal bands)')
	parser.add_option('--EM',
                  action='store_false', dest='expectation_maximisation', default=True,
                  help='do not use the EM algorithm on the character-position matrix (default: uses the EM algorithm)')
	parser.add_option('--Hungarian',
                  action='store_false', dest='hungarian_method', default=True,
                  help='do not use the Hungarian method, but assign characters ' \
				  		'to positions by characters with lowest entropy first to solve the assignment problem' \
				  		' (default: uses the Hungarian method to solve the assignment problem)')
	parser.add_option('-p', '--padding',
                  action='store', dest='padding', type='int', default=0,
                  help='padding with given number of beginning and end markers (default: %default, i.e., no padding)')
	parser.add_option('-s', '--silent',
                  action='store_true', dest='silent', default=False,
                  help='runs in silent mode, just output statistics')
	parser.add_option('-v', '--verbose',
                  action='store_true', dest='verbose', default=False,
                  help='runs in verbose mode')
						
	(options, args) = parser.parse_args()
	return options, args

###############################################################################

def main(file=sys.stdin):
	# if True: tracedot = Dots(1000)
	n, passed = 0, 0
	for line in file:
		# if True: tracedot.trace()
		if line.startswith('#') or line.strip() == '':
			continue
		n += 1
		terms = line.rstrip('\n').split(':')						# Split A:B::C:D into 5 terms A, B, '', C, D.
		# terms = ( term.strip().decode('utf8') for term in terms )	# Eliminate initial and final blanks and convert to unicode.
		terms = ( term.strip() for term in terms )	# Eliminate initial and final blanks and convert to unicode.
		terms = [ term for (i, term) in enumerate(terms) if i != 2 ]# Delete the dummy argument (the one between ::).
#		terms = [ term+term for term in terms ]						# Reduplicating terms.
#		terms = slicing(terms)										# Slicing by symbol.
#		terms = padding(terms)										# Padding by prefix symbols.
#		if options.padding != 0:
#			terms = [ '<'*options.padding+term+'>'*options.padding for term in terms ]# Padding by beginning and end symbols.
		if __trace__: print(__nlg_fmt__ % tuple(terms))
		solution = terms[-1] if terms[-1] != 'None' else None
		solns = Analogy(*(terms[:-1])).Solve(solution=solution)
		if terms[3] in solns:
			passed += 1
		else:
			for elt in solns: break # now elt is an element from the set of solutions solns
			ss = '{ ' + ', '.join(solns) + ' }' if len(solns) > 1 else elt if len(solns) == 1 else "{}"
			if not options.silent: print (__nlg_fmt__ + u' != %s') % (tuple(terms) + (ss, ))
	return passed, n

if __name__ == '__main__':
	options, args = read_argv()
	__verbose__ = options.verbose
	p, n = main()
	print(u'Success: %d / %d = %d %%.' % (p, n, int((float(p)/n)*100)))

