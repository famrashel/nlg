#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import setuptools

from setuptools import setup, Extension

setup(name = 'nlg',
	version = '3.3.0',
	description = 'Python package for manipulation of analogy, extracting analogical clusters, and constructing analogical grids',
	author = 'Rashel Fam & Rudali Huidrom & Yves Lepage',
	author_email = 'fam.rashel@fuji.waseda.jp & rudali.huidrom@ruri.waseda.jp &  yves.lepage@waseda.jp',
	ext_modules =	[Extension('_nlg',
						sources = ['nlg/analogy_in_C/C/nlg.i', 'nlg/analogy_in_C/C/nlg.c', 'nlg/analogy_in_C/C/utf8.c'],
						# swig_opts=['-modern', '-new_repr'], # Comment this line if you have newer version of swig
						extra_compile_args = ['-std=c99']),
					 Extension('_nlgclu',
						sources = ['nlg/nlgCluster/nlgclu_in_C/nlgclu.i', 'nlg/nlgCluster/nlgclu_in_C/nlgclu.c'],
						# swig_opts=['-modern', '-new_repr'] # Comment this line if you have newer version of swig
					)],
	# packages=['nlg'],
	packages = setuptools.find_packages(),
	install_requires=[
		  'tabulate',
          'numpy',
		  'matplotlib'
      ],
	python_requires = '>=3.5'
	)
