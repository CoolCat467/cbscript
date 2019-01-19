import copy
from scratch_tracker import scratch_tracker
from selector_definition import selector_definition

def isNumber(s):
	try:
		float(s)
		return True
	except ValueError:
		return False
		
class environment(object):
	def __init__(self, global_context):
		self.dollarid = {}
		self.global_context = global_context
		self.scratch = scratch_tracker(global_context)
		self.locals = []
		self.selectors = {}
		self.self_selector = None
		
	def clone(self, new_function_name = None):
		new_env = environment(self.global_context)
		
		for id in self.selectors:
			new_env.selectors[id] = self.selectors[id]
		
		new_env.dollarid = copy.deepcopy(self.dollarid)
		if new_function_name == None:
			new_env.scratch = self.scratch
			new_env.locals = self.locals
		else:
			new_env.scratch.prefix = self.global_context.get_scratch_prefix(new_function_name)
			
		new_env.self_selector = self.self_selector
		
		return new_env
		
	def register_local(self, local):
		if local not in self.locals:
			self.locals.append(local)
		
	def apply(self, text):
		text = self.apply_replacements(text)
		text = self.compile_selectors(text)
		
		return text
		
	def apply_replacements(self, text):
		for identifier in reversed(sorted(self.dollarid.keys())):
			text = str(text).replace('$' + identifier, str(self.dollarid[identifier]))	
				
		return text
	
	def set_dollarid(self, id, val):
		if len(id) == 0:
			raise Exception('Dollar ID is empty string.')
		
		if id[0] == '$':
			id = id[1:]
			
		self.dollarid[id] = val
		
	def copy_dollarid(self, id, copyid):
		if len(id) == 0:
			raise Exception('Dollar ID is empty string.')
		
		if id[0].startswith('$'):
			id = id[1:]
		
		if copyid.startswith('$'):
			copyid = copyid[1:]
			
		self.dollarid[id] = self.dollarid[copyid]
		
	def set_atid(self, id, fullselector):
		self.selectors[id] = selector_definition(fullselector, self)
		
		return self.selectors[id]
	
	def compile_selectors(self, command):
		ret = ""
		for fragment in self.split_selectors(command):
			if fragment[0] == "@":
				ret = ret + self.compile_selector(fragment)
			else:
				ret = ret + fragment
				
		return ret		
	
	def get_selector_parts(self, selector):
		if len(selector) == 2:
			selector += "[]"
		
		start = selector[0:3]
		end = selector[-1]
		middle = selector[3:-1]

		parts = middle.split(',')
		
		return start, [part.strip() for part in parts], end
		
	def compile_selector(self, selector):
		sel = selector_definition(selector, self)
		interpreted = sel.compile()
		
		if len(interpreted) == 4:
			# We have @a[] or similar, so truncate
			interpreted = interpreted[:2]
		
		return interpreted
		
	def get_python_env(self):
		return self.dollarid
		
	def register_objective(self, objective):
		if len(objective) > 16:
			raise Exception('Objective name "{0}" is {1} characters long, max is 16.'.format(objective, len(objective)))
		self.global_context.register_objective(objective)
		
	def split_selectors(self, line):
		fragments = []
		
		remaining = str(line)
		while '@' in remaining:
			parts = remaining.split('@', 1)
			if len(parts[0]) > 0:
				fragments.append(parts[0])

			end = 0
			for i in range(len(parts[1])):
				if parts[1][i].isalnum() or parts[1][i] == '_':
					end += 1
				elif parts[1][i] == '[':
					end = parts[1].find(']')+1
					break
				else:
					break
					
			fragments.append('@' + parts[1][:end])
			remaining = parts[1][end:]
						
		if len(remaining) > 0:
			fragments.append(remaining)
			
		#print(line, fragments)
		
		return fragments
		
	def update_self_selector(self, selector):
		if selector[0] != '@':
			return
			
		id = selector[1:]
		if '[' in id:
			id = id.split('[',1)[0]
			
		if id in self.selectors:
			self.self_selector = self.selectors[id]
			
	def register_objective(self, objective):
		self.global_context.register_objective(objective)
		
	def register_array(self, name, from_val, to_val):
		self.global_context.register_array(name, from_val, to_val)
		
	def register_block_tag(self, name, blocks):
		self.global_context.register_block_tag(name, blocks)
		
	def get_scale(self):
		return self.global_context.scale
		
	def set_scale(self, scale):
		self.global_context.scale = scale
		
	scale = property(get_scale, set_scale)
	
	@property
	def arrays(self):
		return self.global_context.arrays
	
	@property
	def block_tags(self):
		return self.global_context.block_tags
	
	@property
	def namespace(self):
		return self.global_context.namespace
	
	@property
	def macros(self):
		return self.global_context.macros
		
	@property
	def template_functions(self):
		return self.global_context.template_functions

	@property
	def functions(self):
		return self.global_context.functions
		
	def get_scratch(self):
		return self.scratch.get_scratch()
	
	def get_scratch_vector(self):
		return self.scratch.get_scratch_vector()
		
	def is_scratch(self, var):
		return self.scratch.is_scratch(var)
	
	def free_scratch(self, id):
		self.scratch.free_scratch(id)
		
	def get_temp_var(self):
		return self.scratch.get_temp_var()
		
	def free_temp_var(self):
		self.scratch.free_temp_var()
		
	def add_constant(self, val):
		return self.global_context.add_constant(val)
		
	def allocate_rand(self, val):
		self.global_context.allocate_rand(val)
	
	def get_friendly_name(self):
		return self.global_context.get_friendly_name()
		
	def get_random_objective(self):
		return self.global_context.get_random_objective()
		
	def register_function(self, name, func):
		self.global_context.register_function(name, func)
	
	def get_unique_id(self):
		return self.global_context.get_unique_id()
		
	def register_clock(self, name):
		self.global_context.register_clock(name)
		
	def get_arrayconst_var(self, name, idxval):
		if name not in self.arrays:
			print('Tried to use undefined array "{}"'.format(name))
			return None
				
		from_val, to_val = self.arrays[name]
		
		index = int(self.apply_replacements(idxval))
		
		if index < from_val or index >= to_val:
			if from_val == 0:
				print('Tried to index {} outside of array {}[{}]'.format(index, name, to_val))
			else:
				print('Tried to index {} outside of array {}[{} to {}]'.format(index, name, from_val, to_val))

		return '{}{}'.format(name, index)
		
	def get_selector_definition(self, selector_text):
		return selector_definition(selector_text, self)