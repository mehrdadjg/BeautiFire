from enum import Enum
import re, string

class Align(Enum):
	LEFT = 0x0
	RIGHT = 0x1
	CENTER = 0x2
	STRETCH = 0x4

class Segment:
	def __init__(self, raw_text, function):
		self.raw_text = raw_text
		self.function = function
	
	def __repr__(self):
		return '<Segment ' + self.function.name + ': "' + self.raw_text + '">'

class Token:
	def __init__(self, text, attached_to_previous = False):
		self.text = text
		self.attached_to_previous = attached_to_previous
	
	def __repr__(self):
		return '<Token "' + self.text + '">'
	
class SegmentFunction(Enum):
	NORMALTEXT = 0x0
	SINGLELINE = 0x1
	

# By putting some string in between $ signs you will force it to be shown in the same line, if possible.
class BeautiFire:

	def __init__(self):
		## page related dimensions
		self.page_width = 80
		
		## text related dimensions
		self.par_first_line_indent = 4
		self.par_other_lines_indent = 0
		self.tab_width = 4
		
		## global paragraph properties
		self.par_alignment = Align.LEFT
	
	def set_page_width(self, page_width):
		self.page_width = page_width
	
	def print_paragraph(self, parahraph, indent=0):
		## Handling boundary cases
		if parahraph.strip() == '':
			print()
			return
		elif '\n' in parahraph:
			raise ValueError("Paragraph contains a new line character.")
		
		## Segmentation: A segment is a maximal part of the text that has
		## a specific functionality.
		special_reg = re.compile(r"\$")
		segments = special_reg.split(parahraph)
		
		index = 0
		segment_function = SegmentFunction.SINGLELINE if parahraph[0] == '$' else SegmentFunction.NORMALTEXT
		
		while index < len(segments):
			if len(segments[index]) == 0:
				segments[index] = Segment(segments[index], segment_function)
				index = index + 1
				segment_function = SegmentFunction(1 - segment_function.value)
			elif segments[index][-1] == '\\':
				if len(segments) > index + 1:
					segments[index] = segments[index][:-1] + '$' + segments[index + 1]
					del segments[index + 1]
			else:
				segments[index] = Segment(segments[index], segment_function)
				index = index + 1
				segment_function = SegmentFunction(1 - segment_function.value)
		# End of Segmentation
		
		tokens = []
		for seg_index in range(len(segments)):
			segment = segments[seg_index]
			if segment.function == SegmentFunction.NORMALTEXT:
				first = True
				for word in re.split('|'.join(string.whitespace), segment.raw_text):
					if word != '':
						if first:
							if segment.raw_text[0] in string.whitespace:
								tokens.append((word, False))
							else:
								tokens.append((word, True))
							first = False
						else:
							tokens.append((word, False))
			elif segment.function == SegmentFunction.SINGLELINE:
				if seg_index > 0:
					previous_segment = segments[seg_index - 1]
					if previous_segment.raw_text[-1] in string.whitespace:
						tokens.append((segment.raw_text, False))
					else:
						tokens.append((segment.raw_text, True))
				else:
					tokens.append((segment.raw_text, True))
		
		index = 0
		line = ''
		line_start = True
		while index < len(tokens):
			newToken = {False:' ', True:''}[tokens[index][1]] + tokens[index][0]
			if len(line + newToken) <= self.page_width:
				line = line + newToken
				index = index + 1
			else:
				print(len(line))
				print(line)
				line = ''

if __name__ == '__main__':
	input()