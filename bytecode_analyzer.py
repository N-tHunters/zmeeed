import dis
import marshal
import json
import sys

code_type = type((lambda x:x).__code__)

class Node:
	def __init__(self, _id, value, analyzer):
		self.id = _id
		self.value = [value,]
		self.nodes = analyzer.nodes
		self.nodes_dict = analyzer.nodes_dict
		self.edges = analyzer.edges
		self.nodes.append(_id)
		self.nodes_dict[_id] = self

		self.in_nodes = []
		self.out_nodes = []

	def is_single(self):
		if len(self.out_nodes) == 1:
			if len(self.nodes_dict[self.out_nodes[0][0]].in_nodes) == 1:
				return True
		return False

	def collapse(self):
		out = self.nodes_dict[self.out_nodes[0][0]]
		self.value = self.value + out.value
		del self.edges[self.edges.index(self.out_nodes[0][1])]
		self.out_nodes = out.out_nodes[::]
		del self.nodes[self.nodes.index(out.id)]
		del self.nodes_dict[out.id]
		for i in self.out_nodes:
			i[1].id_1 = self.id
		del out

	def __str__(self):
		return '\n'.join([str(i) for i in self.value])


class Edge:
	def __init__(self, id_1, id_2, color, analyzer):
		self.id_1 = id_1
		self.id_2 = id_2
		self.color = color

		analyzer.nodes_dict[id_1].out_nodes.append([id_2, self])
		analyzer.nodes_dict[id_2].in_nodes.append(id_1)
		
		analyzer.edges.append(self)


class BytecodeAnalyzer:
	def __init__(self, filename):
		self.filename = filename
		self.nodes = []
		self.nodes_dict = {}
		self.edges = []
		self.data = {}

	def analyze(self):
		code = read_bytecode(self.filename)
		code_c = code

		jump_ops = (
			'POP_JUMP_IF_FALSE',
			'POP_JUMP_IF_TRUE',
			'JUMP_FORWARD',
			'JUMP_ABSOLUTE'
		)

		self.nodes_dict = {}
		self.nodes = []
		self.edges = []

		bytecode = dis.Bytecode(code)
		bytecode = list(bytecode)

		for i in range(len(bytecode)):
			self.addNode(str(i), bytecode[i])

		for i in range(len(bytecode)):
			opname = bytecode[i].opname
			argval = bytecode[i].argval
			if opname != 'RETURN_VALUE':
				if opname == 'JUMP_FORWARD':
					self.addEdge(str(i), str(argval // 2), color='blue')
				elif opname == 'POP_JUMP_IF_FALSE':
					self.addEdge(str(i), str(argval // 2), color='green')
					self.addEdge(str(i), str(i + 1), color='red')
				elif opname == 'POP_JUMP_IF_TRUE':
					self.addEdge(str(i), str(argval // 2), color='green')
					self.addEdge(str(i), str(i + 1), color='red')
				elif opname == 'JUMP_ABSOLUTE':
					self.addEdge(str(i), str(argval // 2), color='blue')
				elif opname == 'FOR_ITER':
					self.addEdge(str(i), str(argval // 2), color='green')
					self.addEdge(str(i), str(i + 1), color='red')
				else:
					self.addEdge(str(i), str(i + 1))

		i = 0
		while i < len(self.nodes):
			node = self.nodes_dict[self.nodes[i]]
			if node.is_single():
				node.collapse()
				i -= 1
			i += 1

		data = {'blocks':[], 'jumps':[], 'consts':[]}

		for i in self.nodes:
			code = [{'offset':j.offset, 'opname':j.opname, 'argval':j.argval, 'argtype':get_type(j.argval)} for j in self.nodes_dict[i].value]
			for j in range(len(code)):
				code[j]['argval'] = str(code[j]['argval'])
				if code[j]['opname'] in jump_ops:
					code[j]['jmpval'] = str(self.nodes.index(str(int(code[j]['argval']) // 2)))
			data['blocks'].append({'code':code})

		for i in self.edges:
			if i.color == 'blue':
				t = 0
			elif i.color == 'green':
				t = 1
			elif i.color == 'red':
				t = -1
			a = i.id_1
			b = i.id_2
			data['jumps'].append([[self.nodes.index(a), self.nodes.index(b)], t])

		data['consts'] = list(map(lambda x:[str(x), get_type(x)], code_c.co_consts))

		self.data = data

		self.edges = []
		self.nodes = []
		self.nodes_dict = []

	def addNode(self, _id, value):
		Node(_id, value, self)

	def addEdge(self, id_1, id_2, **kwargs):
		Edge(id_1, id_2, kwargs.get('color', 'black'), self)

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

def get_type(obj):
	if type(obj) == int:
		return 'int'
	elif type(obj) == str:
		return 'str'
	elif obj == None:
		return 'None'
	elif type(obj) == tuple:
		return 'tuple'
	elif type(obj) == list:
		return 'list'
	elif type(obj) == dict:
		return 'dict'
	elif type(obj) == code_type:
		return 'code'
	print(obj)
	return 'unkown type'