#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Script generates cv in less, sass, scss and css format based on properties file.

Apache License Version 2.0

https://github.com/mwilczek-net/css-cv
"""

import re
import argparse
import validators
import sass
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
	
	@staticmethod
	def parseArgs():
		parser = argparse.ArgumentParser()
		parser.add_argument("file", help="*.properties file to be processed")
		return parser.parse_args()

	@staticmethod
	def processFile(options):
		generated = Property('', -1)
		fileContent = []
		with open(options['file'], "r") as f:
			for line in f:
				if line.strip() == "":
					continue
				fileContent.append(line)
				splited = ProcessingUtils.split_property(line)
				generated.put(splited)
		options['fileContent'] = fileContent
		options['generated'] = generated
	
	@staticmethod
	def getFileName(options):
		try:
			fileName = re.search("^(.*)\.[^/\\\]+$", options['file']).group(1)
		except:
			fileName = options['file']
		options['fileName'] = fileName


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


class BaseFormatter:
	def __init__(self, options):
		self.options = options
		self.parse()
		self.format()
	
	def saveParsed(self):
		with open(self.getSaveFileName(), "w") as file:
			file.write(self.getParsed())
			
	def saveFormated(self):
		with open(self.getSaveFileName() + '.html', "w") as file:
			file.write(self.getFormated())
		
	def format(self):
		lexer = self.getLexer()
		formatter = HtmlFormatter(
			full=True,
			cssclass="source",
			style='trac',
		)
		self.setFormated(highlight(self.getParsed(), lexer, formatter))
	
	def getSaveFileName(self):
		raise NotImplementedError()	
	
	def getParsed(self):
		raise NotImplementedError()
	
	def parse(self):
		raise NotImplementedError()
	
	def getFormated(self):
		raise NotImplementedError()
		
	def setFormated(self, formated):
		pass
		
	def getLexer():
		pass


class PropertiesFormatter(BaseFormatter):
	
	def parse(self):
		pass
	
	def saveParsed(self):
		pass
		
	def getParsed(self):
		return "".join(self.options['fileContent'])
		
	def getSaveFileName(self):
		return self.options['file']
	
	def getFormated(self):
		return self.options['formatedProperties']
		
	def getLexer(self):
		return get_lexer_by_name('properties')
		
	def setFormated(self, formated):
		self.options['formatedProperties'] = formated


class LessFormatter(BaseFormatter):
	def getSaveFileName(self):
		return self.options['fileName'] + ".less"
	
	def getParsed(self):
		return self.options['parsedLess']
	
	def parse(self):
		self.options['generated'].setFormatLess()
		self.options['parsedLess'] = str(self.options['generated'])
	
	def getFormated(self):
		return self.options['formatedLess']
		
	def getLexer(self):
		return get_lexer_by_name('less')
		
	def setFormated(self, formated):
		self.options['formatedLess'] = formated


class SassFormatter(BaseFormatter):
	def getSaveFileName(self):
		return self.options['fileName'] + ".sass"
	
	def getParsed(self):
		return self.options['parsedSass']
	
	def parse(self):
		self.options['generated'].setFormatSass()
		self.options['parsedSass'] = str(self.options['generated'])
	
	def getFormated(self):
		return self.options['formatedSass']
		
	def getLexer(self):
		return get_lexer_by_name('sass')
		
	def setFormated(self, formated):
		self.options['formatedSass'] = formated
		

class ScssFormatter(BaseFormatter):
	def getSaveFileName(self):
		return self.options['fileName'] + ".scss"
	
	def getParsed(self):
		return self.options['parsedScss']
	
	def parse(self):
		self.options['generated'].setFormatLess()
		self.options['parsedScss'] = str(self.options['generated'])
	
	def getFormated(self):
		return self.options['formatedScss']
		
	def getLexer(self):
		return get_lexer_by_name('scss')
		
	def setFormated(self, formated):
		self.options['formatedScss'] = formated
		

class CssFormatter(BaseFormatter):
	def getSaveFileName(self):
		return self.options['fileName'] + ".css"
	
	def getParsed(self):
		return self.options['parsedCss']
	
	def parse(self):
		self.options['generated'].setFormatLess()
		self.options['parsedCss'] = sass.compile(
			string = str(self.options['generated']),
			output_style = "expanded"
		)
	
	def getFormated(self):
		return self.options['formatedCss']
		
	def getLexer(self):
		return get_lexer_by_name('css')
		
	def setFormated(self, formated):
		self.options['formatedCss'] = formated


def cssCVmain():
	args = ProcessingUtils.parseArgs()
	
	options = {
		'file': args.file
	}
	
	ProcessingUtils.getFileName(options)
	ProcessingUtils.processFile(options)
	
	properties = PropertiesFormatter(options)
	properties.saveFormated()

	less = LessFormatter(options)
	less.saveParsed()
	less.saveFormated()

	sass = SassFormatter(options)
	sass.saveParsed()
	sass.saveFormated()

	scss = ScssFormatter(options)
	scss.saveParsed()
	scss.saveFormated()

	css = CssFormatter(options)
	css.saveParsed()
	css.saveFormated()

cssCVmain()

