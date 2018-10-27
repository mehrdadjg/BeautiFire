from enum import Enum
import re, string

class Align(Enum):
	###	In the left alignment, the start indent of a line will appear
	#	on the left side of the text and the end spacing will appear
	#	on the right side of the text.
	LEFT = 0x0
	###	In the right alignment, the start indent of a line will appear
	#	on the right side of the text and the end spacing will appear
	#	on the left side of text.
	RIGHT = 0x1
	###	In the center alignment, the spaces appear like the left
	#	alignment.
	#	If the text (and the surrounding spaces) cannot be completely
	#	centered then they will be shifted on space to the left.
	CENTER = 0x2
	###	Not implemented yet.
	STRETCH = 0x4

class Segment:
	def __init__(self, raw_text, function):
		self.raw_text = raw_text
		self.function = function
	
	def __repr__(self):
		return '<Segment ' + self.function.name + ': "' + self.raw_text + '">'

class Token:
	def __init__(self, text, attached_to_previous_token = False):
		self.text = text
		self.attached_to_previous_token = attached_to_previous_token
	
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
		
		## spacing dimensions
		self.par_first_line_start_indent = 4
		self.par_first_line_end_spacing = 0
		self.par_other_lines_start_indent = 0
		self.par_other_lines_end_spacing = 0
		
		## special characters properties
		self.tab_width = 4
		
		## global paragraph properties
		self.par_alignment = Align.LEFT
	
	def set_page_width(self, page_width):
		self.page_width = page_width
	
	def set_paragraph_alignment(self, par_alignment):
		self.par_alignment = par_alignment
	
	def set_first_line_spacings(self, start_indent = 4, end_spacing = 0):
		self.par_first_line_start_indent = start_indent
		self.par_first_line_end_spacing = end_spacing
	
	def set_other_lines_spacings(self, start_indent = 0, end_spacing = 0):
		self.par_other_lines_start_indent = start_indent
		self.par_other_lines_end_spacing = end_spacing
	
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
		
		## Tokening: tokens are the building blocks of segments.
		tokens = []
		for seg_index in range(len(segments)):
			segment = segments[seg_index]
			if segment.function == SegmentFunction.NORMALTEXT:
				first = True
				for word in re.split('|'.join(string.whitespace), segment.raw_text):
					if word != '':
						if first:
							# If the segment's raw text starts with whitespace, then the first
							# token must not be attached to the previous token
							if segment.raw_text[0] in string.whitespace:
								tokens.append(Token(word))
							else:
								tokens.append(Token(word, attached_to_previous_token=True))
							first = False
						else:
							tokens.append(Token(word))
			elif segment.function == SegmentFunction.SINGLELINE:
				if seg_index > 0:
					previous_segment = segments[seg_index - 1]
					if previous_segment.raw_text[-1] in string.whitespace:
						tokens.append(Token(segment.raw_text))
					else:
						tokens.append(Token(segment.raw_text, attached_to_previous_token=True))
				else:
					tokens.append(Token(segment.raw_text, attached_to_previous_token=True))
		# End of Tokening
		
		# TEST: print header
		print("|" + "_" * (self.page_width - 2) + "|")
		# END TEST
		## Printing
		index = 0
		line = ''
		first_token = True
		line_text_width = self.page_width - (self.par_first_line_start_indent + self.par_first_line_end_spacing)
		first_line = True
		while index < len(tokens):
			if first_token:
				newToken = tokens[index].text
				first_token = False
			else:
				newToken = {False:' ', True:''}[tokens[index].attached_to_previous_token] + tokens[index].text
			
			if len(line + newToken.replace('\t', ' ' * self.tab_width)) <= line_text_width:
				line = line + newToken.replace('\t', ' ' * self.tab_width)
				index = index + 1
			else:
				if self.par_alignment == Align.LEFT:
					if first_line:
						print(' ' * self.par_first_line_start_indent + line + ' ' * self.par_first_line_end_spacing)
						first_line = False
					else:
						print(' ' * self.par_other_lines_start_indent + line + ' ' * self.par_other_lines_end_spacing)
				elif self.par_alignment == Align.RIGHT:
					if first_line:
						print(('{:>' + str(self.page_width) + '}').format(' ' * self.par_first_line_end_spacing + line + ' ' * self.par_first_line_start_indent))
						first_line = False
					else:
						print(('{:>' + str(self.page_width) + '}').format(' ' * self.par_other_lines_end_spacing + line + ' ' * self.par_other_lines_start_indent))
				elif self.par_alignment == Align.CENTER:
					if first_line:
						print(('{:^' + str(self.page_width) + '}').format(' ' * self.par_first_line_start_indent + line + ' ' * self.par_first_line_end_spacing))
						first_line = False
					else:
						print(('{:^' + str(self.page_width) + '}').format(' ' * self.par_other_lines_start_indent + line + ' ' * self.par_other_lines_end_spacing))
				
				line = ''
				first_token = True
				line_text_width = self.page_width - (self.par_other_lines_start_indent + self.par_other_lines_end_spacing)
		
		if self.par_alignment == Align.LEFT:
			if first_line:
				print(' ' * self.par_first_line_start_indent + line + ' ' * self.par_first_line_end_spacing)
			else:
				print(' ' * self.par_other_lines_start_indent + line + ' ' * self.par_other_lines_end_spacing)
		elif self.par_alignment == Align.RIGHT:
			if first_line:
				print(('{:>' + str(self.page_width) + '}').format(' ' * self.par_first_line_end_spacing + line + ' ' * self.par_first_line_start_indent))
			else:
				print(('{:>' + str(self.page_width) + '}').format(' ' * self.par_other_lines_end_spacing + line + ' ' * self.par_other_lines_start_indent))
		elif self.par_alignment == Align.CENTER:
			if first_line:
				print(('{:^' + str(self.page_width) + '}').format(' ' * self.par_first_line_start_indent + line + ' ' * self.par_first_line_end_spacing))
			else:
				print(('{:^' + str(self.page_width) + '}').format(' ' * self.par_other_lines_start_indent + line + ' ' * self.par_other_lines_end_spacing))
		# End of Printing
if __name__ == '__main__':
	input()