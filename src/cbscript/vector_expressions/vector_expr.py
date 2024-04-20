class vector_expr:
	def __init__(self, exprs):
		self.exprs = exprs

	def compile(self, func, assignto):
		vars = []
		for i in range(3):
			var = self.exprs[i].compile(func, None if assignto is None else assignto[i])

			if var is None:
				return None

			vars.append(var)

		return vars
