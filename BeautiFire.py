import re, string

LEFT = 0x1
RIGHT = 0x2
CENTER = 0x4
STRETCH = 0x8

# By putting some string in between $ signs you will force it to be shown in the same line, if possible.
class BeautiFire:

	def __init__(self):
		self.terminal_width = 80
		self.paragraph_second_line_indent = 4
		self.short_line_policy = LEFT
	
	def set_terminal_width(self, terminal_width):
		self.terminal_width = terminal_width
	
	def print_paragraph(self, parahraph, indent=0):
		if parahraph.strip() == '':
			print()
			return
		elif '\n' in parahraph:
			raise ValueError("Paragraph contains a new line character.")
		special_reg = re.compile(r"\$")
		
		segments = special_reg.split(parahraph)
		
		index = 0
		isSingleLine = True if parahraph[0] == '$' else False
		
		while index < len(segments):
			if len(segments[index]) == 0:
				segments[index] = [segments[index], isSingleLine]
				index = index + 1
				isSingleLine = not isSingleLine
			elif segments[index][-1] == '\\':
				if len(segments) > index + 1:
					segments[index] = segments[index][:-1] + '$' + segments[index + 1]
					del segments[index + 1]
			else:
				segments[index] = [segments[index], isSingleLine]
				index = index + 1
				isSingleLine = not isSingleLine
		
		tokens = []
		for seg_index in range(len(segments)):
			segment = segments[seg_index]
			if segment[1] == False:
				first = True
				for word in re.split('|'.join(string.whitespace), segment[0]):
					if word != '':
						if first:
							if segment[0][0] in string.whitespace:
								tokens.append((word, False))
							else:
								tokens.append((word, True))
							first = False
						else:
							tokens.append((word, False))
			else:
				if seg_index > 0:
					if segments[seg_index - 1][0][-1] in string.whitespace:
						tokens.append((segment[0], False))
					else:
						tokens.append((segment[0], True))
				else:
					tokens.append((segment[0], True))
		
		index = 0
		line = ''
		line_start = True
		while index < len(tokens):
			newToken = {False:' ', True:''}[tokens[index][1]] + tokens[index][0]
			if len(line + newToken) <= self.terminal_width:
				line = line + newToken
				index = index + 1
			else:
				print(len(line))
				print(line)
				line = ''

if __name__ == '__main__':
	input()