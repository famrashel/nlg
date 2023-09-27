#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from posixpath import split
import sys
import time
import argparse
import tkinter as tk

import nlg.NlgSymbols as NlgSymbols

from tkinter.filedialog import askopenfilename, asksaveasfilename

###############################################################################

__author__ = 'Fam Rashel <fam.rashel@fuji.waseda.jp>'

__date__, __version__ = '24/06/2021', '0.10' # Creation

__description__ = 'GUI program for analogy'

__verbose__ = True		# Gives information about timing, etc. to the user.
__trace__ = False		# To be used by the developper for debugging.

###############################################################################

class Excel(tk.Frame):
	def __init__(self, master, rows=10, columns=20, width=8):
		super().__init__(master)

		for i in range(columns):
			self.make_entry(0, i+1, width, f'C{i}', False) 

		for row in range(rows):
			self.make_entry(row+1, 0, 5, f'R{row}', False)
				
			for column in range(columns):
				self.make_entry(row+1, column+1, width, '', True)
		
		self.n_row = rows
		self.n_column = columns
	
	def fromFile(self, line):
		input = [ x for y in line.split(NlgSymbols.conformity) for x in y.split(NlgSymbols.ratio) ]

		for idx, val in enumerate[input]:
			if val != 'None':
				self.children[idx] = val

	def make_entry(self, row, column, width, text, state):
		e = tk.Entry(self, width=width)
		if text: e.insert(0, text)
		e['state'] = tk.NORMAL if state else tk.DISABLED
		e.coords = (row-1, column-1)
		e.grid(row=row, column=column)

###############################################################################

def donothing():
	x = 0

def create_menubar(master):
	menu_bar = tk.Menu(master)

	filemenu = tk.Menu(menu_bar, tearoff=0)
	filemenu.add_command(label="New", command=donothing)
	filemenu.add_command(label="Open", command=lambda: open_file(master))
	filemenu.add_command(label="Save As...", command=lambda: saveas_file(master))
	filemenu.add_separator()
	filemenu.add_command(label="Exit", command=master.quit)
	menu_bar.add_cascade(label="File", menu=filemenu)

	helpmenu = tk.Menu(menu_bar, tearoff=0)
	helpmenu.add_command(label="Help Index", command=donothing)
	helpmenu.add_command(label="About...", command=donothing)
	menu_bar.add_cascade(label="Help", menu=helpmenu)

	return menu_bar

def open_file(master, excel):
	"""Open a file for editing."""

	filepath = askopenfilename(
		filetypes=[("Grid Files", "*.grid"), ("All Files", "*.*")]
	)
	if not filepath:
		return

	# txt_edit.delete("1.0", tk.END)
	with open(filepath, "r") as input_file:
		text = input_file.read()
		excel.fromFile(text.strip())

	master.title(f"Simple Text Editor - {filepath}")

def saveas_file(master):
	"""Save the current file as a new file."""

	filepath = asksaveasfilename(
		defaultextension="grid",
		filetypes=[("Grid Files", "*.grid"), ("All Files", "*.*")]
	)
	if not filepath:
		return

	# txt_edit.delete("1.0", tk.END)
	# with open(filepath, "w") as output_file:
	# 	text = input_file.read()
	# 	output_file.write(text)

	master.title(f"Simple Text Editor - {filepath}")

###############################################################################

def read_argv():

	this_version = 'v%s (c) %s %s' % (__version__, __date__.split('/')[2], __author__)
	this_description = __description__
	this_usage = """
	%(prog)s  <  FILE_OF_GRIDS
	"""

	parser = argparse.ArgumentParser(description=this_description, usage=this_usage, epilog=this_version)
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

def convert_time(duration):
	"""
	Convert time data (s) to human-friendly format
	"""
	m, s = divmod(round(duration), 60)
	h, m = divmod(m, 60)
	hms = "%d:%02d:%02d" % (h, m,s)
	return hms

###############################################################################

def _test():
	import doctest
	doctest.testmod()
	sys.exit(0)

def main():
	
	# Window construction
	main_window = tk.Tk()
	main_window.title('VisualNlg')

	# Add menu bar
	main_window.config(menu=create_menubar(main_window))

	# Widgets
	greeting = tk.Label(text="Test label")
	main_window.rowconfigure(0, minsize=10, weight=1)
	main_window.columnconfigure(0, minsize=30, weight=1)
	greeting.grid(row=0, column=0, sticky="ew")

	sheet_canvas = tk.Canvas(main_window)
	main_window.rowconfigure(1, minsize=300, weight=1)
	main_window.columnconfigure(0, minsize=500, weight=1)
	sheet_canvas.grid(row=1, column=0, sticky="news")

	spreadsheet = Excel(sheet_canvas, 10, 10)
	spreadsheet.grid(row=0, column=0, padx=20, pady=20)

	scrollbar = tk.Scrollbar(sheet_canvas, orient='vertical', command=sheet_canvas.yview)
	scrollbar.grid(row=1, column=1, sticky='ns')
	sheet_canvas.configure(yscrollcommand=scrollbar.set)
	

	bt = tk.Button(main_window, text='Dump', command=lambda: show_cells(spreadsheet))
	bt.grid(row=2, column=0, pady=20)

	main_window.mainloop()

def show_cells(ex):
	print('\n--== dumping cells ==--')
	col_count = 0
	for e in ex.children:
		if col_count == ex.n_column:
			print()
			col_count = 0
		v = ex.children[e]
		print(f'{v.get()}', end=' : ')
		col_count += 1
	print()

if __name__ == '__main__':
	options = read_argv()
	if options.test: _test()
	__verbose__ = options.verbose
	__trace__ = options.trace
	t_start = time.time()
	main()
	if __verbose__: print(f'# {os.path.basename(__file__)} - Processing time: {(convert_time(time.time() - t_start))}', file=sys.stderr)