import json
import graphviz

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
			jumps.append(int(i['jmpval']))
			decompiled.append(f'if {condition}: goto {dest}')
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
			jumps.append(int(i['jmpval']))
			decompiled.append(f'if {condition}: goto {dest}')
		elif i['opname'] == 'RETURN_VALUE':
			value = to_str(*stack.pop())
			decompiled.append(f'return {value}')
			returns = True
		else:
			print(i)
	return jumps, decompiled, returns

def decompile(filename):
	with open(filename) as file:
		data = json.load(file)

	decompiled_blocks = []
	edges = []

	for i in range(len(data['blocks'])):
		jumps, decompiled, returns = decompile_block(data['blocks'][i])
		decompiled_blocks.append('\n'.join(decompiled))
		if not returns:
			jumps.append(i + 1)
		for j in jumps:
			edges.append([i, j])
	
	dot = graphviz.Digraph(graph_attr={'splines': 'ortho'}, node_attr={'shape':'box'})
	for i in range(len(decompiled_blocks)):
		dot.node(str(i), decompiled_blocks[i])

	for i in edges:
		dot.edge(str(i[0]), str(i[1]))

	dot.render('output.gv', format='png', view=True)

decompile('out.json')