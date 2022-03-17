import json
import sys
# import graphviz

decompiled_blocks_global = []

class Line:
	def __init__(self, string):
		self.string = string

	def toString(self, indent=0):
		return indent * '\t' + str(self)

	def __str__(self):
		return self.string

class Condition:
	def __init__(self, string):
		self.string = string

	def toString(self, indent=0):
		return indent * '\t' + str(self)

	def __str__(self):
		return self.string

class Block:
	def __init__(self, id, parent=None):
		self.id = id
		self.parent = parent
		self.lines = []

	def addLine(self, line):
		self.lines.append(line)

	def toString(self, indent=0):
		s = []
		for i in self.lines:
			if type(i) == Line:
				s.append(i.toString(indent))
			elif type(i) == list:
				global decompiled_blocks_global
				if i[1].id in decompiled_blocks_global:
					s.append(indent * '\t' + f'if {i[0].toString()}: goto block[{i[1].id}]')
				else:
					decompiled_blocks_global.append(i[1].id)
					s.append(indent * '\t' + f'')
					s.append(i[1].toString(indent + 1))

	def __str__(self):
		return toString(self)

def to_str(value, t):
	if t == 'str':
		return '"' + value + '"'
	return str(value)

def decompile_block(block):
	stack = []
	jumps = []
	decompiled = []
	returns = False
	for i in block['code']:
		if i['opname'] == 'LOAD_NAME':
			stack.append([i['argval'], 'name'])
		elif i['opname'] == 'CALL_FUNCTION':
			func_args = ', '.join([to_str(*stack.pop()) for _ in range(int(i['argval']))][::-1])
			func = stack.pop()[0]
			stack.append([f'{func}({func_args})', 'name'])
		elif i['opname'] == 'STORE_NAME':
			right = to_str(*stack.pop())
			left = i['argval']
			decompiled.append(f'{left} = {right}')
		elif i['opname'] == 'LOAD_CONST':
			stack.append([i['argval'], i['argtype']])
		elif i['opname'] == 'BINARY_SUBSCR':
			index = to_str(*stack.pop())
			obj = stack.pop()[0]
			stack.append([f'{obj}[{index}]', 'exp'])
		elif i['opname'] == 'COMPARE_OP':
			op = i['argval']
			op_right = to_str(*stack.pop())
			op_left = to_str(*stack.pop())
			stack.append([f'({op_left} {op} {op_right})', 'exp'])
		elif i['opname'] == 'POP_JUMP_IF_FALSE':
			condition = to_str(*stack.pop())
			dest = i['argval']
			jumps.append([int(i['jmpval']), 'false'])
			decompiled.append(f'if not {condition}: goto {dest}')
		elif i['opname'] == 'BINARY_ADD':
			op_right = to_str(*stack.pop())
			op_left = to_str(*stack.pop())
			stack.append([f'({op_left} + {op_right})', 'exp'])
		elif i['opname'] == 'POP_TOP':
			decompiled.append(to_str(*stack.pop()))
		elif i['opname'] == 'INPLACE_MULTIPLY':
			op_right = to_str(*stack.pop())
			op_left = to_str(*stack.pop())
			stack.append([f'{op_left} * {op_right}', 'exp'])
		elif i['opname'] == 'POP_JUMP_IF_TRUE':
			condition = to_str(*stack.pop())
			dest = i['argval']
			jumps.append([int(i['jmpval']), 'true'])
			decompiled.append(f'if {condition}: goto {dest}')
		elif i['opname'] == 'RETURN_VALUE':
			value = to_str(*stack.pop())
			decompiled.append(f'return {value}')
			returns = True
		else:
			print(i)
	return jumps, decompiled, returns

def decompile(filename, out_filename):
	with open(filename) as file:
		data = json.load(file)

	decompiled_blocks = []
	edges = []

	for i in range(len(data['blocks'])):
		jumps, decompiled, returns = decompile_block(data['blocks'][i])
		decompiled_blocks.append(decompiled)
		if not returns:
			if len(jumps) == 0:
				jumps.append([i + 1, ''])
			else:
				if jumps[0][1] == 'true':
					jumps.append([i + 1, 'false'])
				else:
					jumps.append([i + 1, 'true'])
		for j in jumps:
			edges.append([i, j])

	data = {
		'blocks':[],
		'jumps':[]
	}

	for i in decompiled_blocks:
		data['blocks'].append(i)

	for i in edges:
		if i[1][1] == 'true':
			color_ind = 1
		elif i[1][1] == 'false':
			color_ind = -1
		else:
			color_ind = 0
		data['jumps'].append([i[0], i[1][0], color_ind])

	with open(out_filename, 'w') as file:
		json.dump(data, file)
	
	# dot = graphviz.Digraph(graph_attr={'splines': 'ortho'}, node_attr={'shape':'box'})
	# for i in range(len(decompiled_blocks)):
	# 	dot.node(str(i), decompiled_blocks[i])

	# for i in edges:
	# 	if i[1][1] == 'true':
	# 		color = 'green'
	# 	elif i[1][1] == 'false':
	# 		color = 'red'
	# 	else:
	# 		color = 'blue'
	# 	dot.edge(str(i[0]), str(i[1][0]), color=color)

	# dot.render('output.gv', format='png', view=True)

if len(sys.argv) != 3:
	print(f'Usage: {sys.argv[0]} <in json path> <out json path>')
else:
	decompile(sys.argv[1], sys.argv[2])