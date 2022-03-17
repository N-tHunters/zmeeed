import dis
import marshal
import json
import sys

nodes = []
nodes_dict = {}
edges = []

class Node:
	def __init__(self, _id, value):
		self.id = _id
		self.value = [value,]
		global nodes
		global nodes_dict
		nodes.append(_id)
		nodes_dict[_id] = self

		self.in_nodes = []
		self.out_nodes = []

	def is_single(self):
		if len(self.out_nodes) == 1:
			if len(nodes_dict[self.out_nodes[0][0]].in_nodes) == 1:
				return True
		return False

	def collapse(self):
		out = nodes_dict[self.out_nodes[0][0]]
		self.value = self.value + out.value
		del edges[edges.index(self.out_nodes[0][1])]
		self.out_nodes = out.out_nodes[::]
		del nodes[nodes.index(out.id)]
		del nodes_dict[out.id]
		for i in self.out_nodes:
			i[1].id_1 = self.id
		del out

	def __str__(self):
		return '\n'.join([str(i) for i in self.value])


class Edge:
	def __init__(self, id_1, id_2, **kwargs):
		self.id_1 = id_1
		self.id_2 = id_2
		global edges
		self.color = kwargs.get('color', 'black')

		nodes_dict[id_1].out_nodes.append([id_2, self])
		nodes_dict[id_2].in_nodes.append(id_1)
		
		edges.append(self)

def read_bytecode(filename):
	i = 16
	while True:
		file = open(filename, 'rb')
		file.read(i)
		try:
			code = marshal.load(file)
			return code
		except:
			pass
		i += 1

def graph(code, data_filename):
	code_c = code
	global nodes_dict
	global nodes
	global edges

	nodes_dict = {}
	nodes = []
	edges = []

	bytecode = dis.Bytecode(code)
	bytecode = list(bytecode)

	for i in range(len(bytecode)):
		Node(str(i), bytecode[i])

	for i in range(len(bytecode)):
		opname = bytecode[i].opname
		argval = bytecode[i].argval
		if opname != 'RETURN_VALUE':
			if opname == 'JUMP_FORWARD':
				Edge(str(i), str(argval // 2), color='blue')
			elif opname == 'POP_JUMP_IF_FALSE':
				Edge(str(i), str(argval // 2), color='green')
				Edge(str(i), str(i + 1), color='red')
			elif opname == 'POP_JUMP_IF_TRUE':
				Edge(str(i), str(argval // 2), color='green')
				Edge(str(i), str(i + 1), color='red')
			elif opname == 'JUMP_ABSOLUTE':
				Edge(str(i), str(argval // 2), color='blue')
			elif opname == 'FOR_ITER':
				Edge(str(i), str(argval // 2), color='green')
				Edge(str(i), str(i + 1), color='red')
			else:
				Edge(str(i), str(i + 1))

	i = 0
	while i < len(nodes):
		node = nodes_dict[nodes[i]]
		if node.is_single():
			node.collapse()
			i -= 1
		i += 1

	data = {'blocks':[], 'jumps':[], 'consts':[]}

	for i in nodes:
		code = [{'offset':j.offset, 'opname':j.opname, 'argval':j.argval} for j in nodes_dict[i].value]
		for j in range(len(code)):
			code[j]['argval'] = str(code[j]['argval'])
		data['blocks'].append({'code':code})

	for i in edges:
		if i.color == 'blue':
			t = 0
		elif i.color == 'green':
			t = 1
		elif i.color == 'red':
			t = -1
		data['jumps'].append([[i.id_1, i.id_2], t])

	data['consts'] = code_c.co_consts

	with open(data_filename, 'w') as file:
		json.dump(data, file)

if len(sys.argv) != 3:
	print(f'Usage: {sys.argv[0]} <pyc path> <json path>')
else:
	graph(read_bytecode(sys.argv[1]), sys.argv[2])