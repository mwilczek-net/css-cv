#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Script generates cv in less, css and pdf format based on properties file
"""

import argparse
import validators
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

INDENT_SIZE = 4
INDENT_STRING = ' '

class ProcessingUtils:
	@staticmethod
	def indent(i):
		if i<0:
			return ''
		return INDENT_STRING*INDENT_SIZE*i

	@staticmethod
	def indent_str(i, *args):
		result = []
		result.append(ProcessingUtils.indent(i))
		for x in args:
			result.append(x)

		return ''.join(result)

	@staticmethod
	def split_property(property):
		property = property.split("=", 1)
		key = property[0].strip().split(".")

		return {
			'keys': key,
			'value': property[1].strip(),
		}

	@staticmethod
	def parse_string(value):
		if validators.email(value):
			return ''.join(['email("',value,'")'])
		elif validators.url(value):
			return ''.join(['url("',value,'")'])
		return value


class Property:
	def __init__(self, name, level):
		self.name = name
		self.level = level
		self.values = []
		self.setFormatLess()

	def setFormat(self, format):
		self.format = format
		for x in self.values:
			try:
				x.setFormat(format)
			except AttributeError:
				pass

	def setFormatLess(self):
		self.setFormat("less")

	def setFormatSass(self):
		self.setFormat("sass")

	def getFormat(self, format):
		return self.format

	def getLineEnd(self):
		return ";" if self.format == "less" else ""

	def getOpening(self):
		return " {" if self.format == "less" else ""

	def getEnding(self):
		return "}" if self.format == "less" else ""

	def getName(self):
		return self.name;

	def getValues(self):
		return self.values;

	def getLevel(self):
		return self.level;

	def nameEquals(nameToEqual):
		return self.name == nameToEqual

	def __str__(self):
		result = []
		prev_object = False
		prev_str = False

		for v in self.getValues():
			if isinstance(v, basestring):
				if self.getLevel()>=0 and prev_object:
					result.append(ProcessingUtils.indent_str(self.getLevel(), self.getEnding()))
				result.append(ProcessingUtils.indent_str(self.getLevel(), self.getName(), ': ', ProcessingUtils.parse_string(str(v)), self.getLineEnd()))
				prev_object = False
				prev_string = True
			else:
				if self.getLevel()>=0 and not prev_object:
					result.append(ProcessingUtils.indent_str(self.getLevel(), self.getName(), self.getOpening()))
				result.append(str(v))
				prev_object = True
				prev_string = False
		
		if self.getLevel()>=0 and prev_object:
			result.append(ProcessingUtils.indent_str(self.getLevel(), self.getEnding()))
		return '\n'.join(result)

	def put(self, property):
		keys = property['keys']
		value = property['value']
		
		if len(keys) == 0:
			self.values.append(value)
		else:
			firstKey = keys.pop(0)
			for k in self.values:
				try:
					if k.getName() == firstKey:
						k.put({'keys': keys, 'value': value})
						return
				except AttributeError:
					pass
			p = Property(firstKey, self.getLevel()+1)
			p.put({'keys': keys, 'value': value})
			self.values.append(p)


def parseArgs():
	parser = argparse.ArgumentParser()
	parser.add_argument("file", help="*.properties file to be processed")
	return parser.parse_args()

def processFile(args):
	generated = Property('', -1)
	with open(args.file, "r") as f:
		for line in f:
			if line.strip() == "":
				continue
			splited = ProcessingUtils.split_property(line)
			generated.put(splited)
	return generated

def getFileName(args):
	splitedByPath = args.file.split("/")
	folder = splitedByPath[0:-1]
	file = ".".join(splitedByPath[-1].split(".")[0:-1])
	folder.append(file)
	return "/".join(folder)
	

def saveLess(fileName, generated):
	generated.setFormatLess()
	with open(fileName+".less", "w") as file:
		file.write(str(generated))

def saveSass(fileName, generated):
	generated.setFormatSass()
	with open(fileName+".sass", "w") as file:
		file.write(str(generated))

def saveScss(fileName, generated):
	generated.setFormatLess()
	with open(fileName+".scss", "w") as file:
		file.write(str(generated))

def formatProperties(args):
	with open(args.file, "r") as f:
		content = f.read()
	
	lexer = get_lexer_by_name('properties')
	formatter = HtmlFormatter(
		full=True,
		cssclass="source",
		style='trac',
	)
	result = highlight(content, lexer, formatter)
	
	with open(args.file+".html", "w") as f:
		f.write(result)

def formatLess(fileName):
	with open(fileName+".less", "r") as f:
		content = f.read()
	
	lexer = get_lexer_by_name('less')
	formatter = HtmlFormatter(
		full=True,
		cssclass="source",
		style='trac',
	)
	result = highlight(content, lexer, formatter)
	
	with open(fileName+".less.html", "w") as f:
		f.write(result)

def formatScss(fileName):
	with open(fileName+".scss", "r") as f:
		content = f.read()
	
	lexer = get_lexer_by_name('scss')
	formatter = HtmlFormatter(
		full=True,
		cssclass="source",
		style='trac',
	)
	result = highlight(content, lexer, formatter)
	
	with open(fileName+".scss.html", "w") as f:
		f.write(result)

def cssCVmain():
	args = parseArgs()
	
	generated = processFile(args)
	formatProperties(args)

	fileName = getFileName(args)

	saveLess(fileName, generated)
	formatLess(fileName)

	saveSass(fileName, generated)

	saveScss(fileName, generated)
	formatScss(fileName)	

cssCVmain()

