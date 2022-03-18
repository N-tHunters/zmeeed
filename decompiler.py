import json
import sys
# import graphviz

decompiled_blocks_global = []


class Token:
	def __init__(self, type, value):
		self.type = type
		self.string = str(value)
		self.value = value

	def __str__(self):
		return self.string


class Line:
	def __init__(self, tokens, number):
		self.tokens = tokens

	def toString(self, indent=0):
		return indent * '\t' + str(self)

	def __str__(self):
		return str(self.tokens)


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

class Decompiler:
	def __init__(self, bytecode_analyzer):
		self.bytecode_analyzer = bytecode_analyzer

	def decompile(self):
		data = self.bytecode_analyzer.data

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

		self.data = data


def to_str(value, t):
	if t == 'str':
		return '"' + value + '"'
	return str(value)


def to_list(op):
	if type(op) == list:
		return op
	return [op,]

def decompile_block(block):
	stack = []
	jumps = []
	decompiled = []
	returns = False
	for i in block['code']:
		if i['opname'] == 'LOAD_NAME':
			# stack.append([i['argval'], 'name'])
			stack.append(Token('name', i['argval']))
		elif i['opname'] == 'CALL_FUNCTION':
			func_args = []
			for j in range(int(i['argval'])):
				func_args.append(to_list(stack.pop()))
				if j < int(i['argval']) - 1:
					func_args.append(Token('arg_delim', ','))
			func = to_list(stack.pop())
			stack.append(func + [Token('call_par_left', '('),] + func_args + [Token('call_par_right', ')'),])
		elif i['opname'] == 'STORE_NAME':
			right = to_list(stack.pop())
			left = i['argval']
			decompiled.append([Token('name', left), Token('assign', '=')] + right)
		elif i['opname'] == 'LOAD_CONST':
			stack.append(Token(i['argtype'], i['argval']))
		elif i['opname'] == 'BINARY_SUBSCR':
			index = to_list(stack.pop())
			obj = to_list(stack.pop())
			stack.append(obj + [Token('ind_par_left', '['),] + index + [Token('ind_par_right', ']'),])
		elif i['opname'] == 'COMPARE_OP':
			op = i['argval']
			op_right = to_list(stack.pop())
			op_left = to_list(stack.pop())
			stack.append(op_right + [Token('comp_op', op),] + op_left)
		elif i['opname'] == 'POP_JUMP_IF_FALSE':
			condition = to_list(stack.pop())
			dest = i['argval']
			jumps.append([int(i['jmpval']), 'false'])
			decompiled.append(Line([Token('if', 'if'), Token('logic_op', 'not')] + condition + [Token('block_begin', ':'), Token('goto', 'goto'), Token('num', dest)]))
		elif i['opname'] == 'BINARY_ADD':
			op_right = to_list(stack.pop())
			op_left = to_list(stack.pop())
			stack.append(op_right + [Token('math_op', '+'),] + op_left)
		elif i['opname'] == 'POP_TOP':
			decompiled.append(Line(to_list(stack.pop())))
		elif i['opname'] == 'INPLACE_MULTIPLY':
			op_right = to_list(stack.pop())
			op_left = to_list(stack.pop())
			stack.append(op_right + [Token('math_op', '*'),] + op_left)
		elif i['opname'] == 'POP_JUMP_IF_TRUE':
			condition = to_list(stack.pop())
			dest = int(i['argval'])
			jumps.append([int(i['jmpval']), 'true'])
			decompiled.append(Line([Token('if', 'if'),] + condition + [Token('block_begin', ':'), Token('goto', 'goto'), Token('num', dest)]))
		elif i['opname'] == 'IMPORT_NAME':
			fromlist = to_list(stack.pop())
			level = to_list(stack.pop())
			module = i['argval']
			e = []
			e.append(Token('name', '__import__'))
			e.append(Token('call_par_left', '('))
			e.append(Token('str_par_left', '\''))
			e.append(Token('string', module))
			e.append(Token('str_par_right', '\''))
			e.append(Token('arg_delim', ','))
			e.append(Token('arg_keyword_key', 'fromlist'))
			if fromlist == None:
				e.append(Token('none', None))
			else:
				e += fromlist
			e.append(Token('arg_delim', ','))
			e.append(Token('arg_keyword_key', 'level'))
			e += level
			e.append(Token('call_par_right', ')'))
			stack.append(e)
		elif i['opname'] == 'BUILD_LIST':
			# elements = [to_list(stack.pop()) for _ in range(int(i['argval']))][::-1]
			elements = []
			for j in range(int(i['argval'])):
				elements.append(to_list(stack.pop()))
				if j < int(i['argval']) - 1:
					elements.append(Token('seq_delim', ','))
			stack.append([Token('list_par_left', '['),] + elements + [Token('list_par_right'), ']'])
		elif i['opname'] == 'STORE_GLOBAL':
			right = to_list(stack.pop())
			left = Token('name', i['argval'])
			decompiled.append(Line([left, Token('assign', '=')] + right))
		elif i['opname'] == 'LOAD_BUILD_CLASS':
			stack.append([Token('name', 'builtins'), Token('get_attr', '.'), Token('name', '__build_class__')])
		elif i['opname'] == 'MAKE_FUNCTION':
			func_name = Token(to_list(stack.pop()).string, 'func_name')
			func_code = Token(to_list(stack.pop()).value, 'code')
			# decompiled.append(f'def {func_name}()')
			decompiled.append(Line([Token('def', 'def'), func_name]))
			stack.append(func_name)
		elif i['opname'] == 'RETURN_VALUE':
			value = to_list(stack.pop())
			decompiled.append(Line([Token('ret', 'return'),] + value))
			returns = True
		else:
			print('Unkown instruction:', i)
	return jumps, decompiled, returns