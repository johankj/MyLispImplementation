import logging
import operator as op

logging.basicConfig(level=logging.INFO)

Symbol = str

class Env(dict):
	def __init__(self, params=(), args=(), outer=None):
		logging.info("new dict, %s, %s", parms, args)
		self.update(zip(params, args))
		self.outer = outer

	def find(self, var):
		"""Find var in self. Go broader if not in innermost."""
		if var in self:
			return self
		else:
			if self.outer:
				return self.outer.find(var)
			else:
				raise NameError("name '%s' is not defined" % var)


SYMBOL_TABLE = Env()
SYMBOL_TABLE.update({
	'+': op.add,
	'-': op.sub,
	'*': op.mul,
	'/': op.div,
	'>': op.gt,
	'<': op.lt,
	'>=': op.ge,
	'<=': op.le,
	'=': op.eq,
	'==': op.eq,
	'/=': op.ne,
	'not': op.not_,
	'eq?': op.is_,
	'length': len,
	':': lambda x, y: [x] + y,
	'head': lambda x: x[0],
	'tail': lambda x: x[1:],
	'append': op.add,
	'list': lambda *x: list(x),
	'list?': lambda x: isinstance(x, list),
	'null?': lambda x: x == [],
	'symbol?': lambda x: isinstance(x, Symbol),
	'map': lambda f, xs: [f(x) for x in xs],
})


def atomize(token):
	"""Convert a token into an atom."""
	try:
		return int(token)
	except ValueError:
		try:
			return float(token)
		except ValueError:
			return token

def lex(s):
	"""
	Parse tokens from a string.
	A token is in the form of either a parenthesis or a string.
	
	Example:
	> list(lex("(if (== 0 0) 1 2)"))
	['(', 'if', '(', '==', 0, 0, ')', 1, 2, ')']
	"""
	tokens = s.replace('(', ' ( ').replace(')', ' ) ').split()

	# Numbers become numbers; every other token is a symbol (str).
	for token in tokens:
		yield atomize(token)


def parse(tokens):
	""""
	Read an expression from a sequence of tokens.

	> parse(iter([1]))
	1
	> parse(iter(['(', ':=', 'x', 1, ')']))
	[':=', 'x', 1]
	>>> parse(iter(['(', 'if', '(', '==', 0, 0, ')', 1, 2, ')']))
	['if', ['==', 0, 0], 1, 2]
	"""
	def parse_expression(tokens):
		expression = []
		for token in tokens:
			if token == '(':
				expression.append(parse_expression(tokens))
			elif token == ')':
				break
			else:
				expression.append(token)
		return expression
	return parse_expression(tokens)[0]


def eval(exp, env=SYMBOL_TABLE):
	"""
	Evaluate a program.

	> eval(1)
	1
	> eval(['if', ['==', 0, 0], 1, 2])
	1
	> eval(['if', ['==', 0, 1], 1, 2])
	2
	"""
	if True or __debug__:
		if env == SYMBOL_TABLE:
			logging.info("eval, %s", exp)
		else:
			logging.info("eval, %s, %s", exp, env)

	# variable reference
	if isinstance(exp, Symbol):
		return [] if exp == "[]" else env.find(exp)[exp]
	# constant literal
	elif not isinstance(exp, list):
		return exp
	else:
		keyword, args = exp[0], exp[1:]
		# conditional
		if keyword == "if":
			test, conseq, alt = args
			return eval(conseq if eval(test, env) else alt, env)
		# definition
		elif keyword == ":=":
			var, expr = args
			env[var] = eval(expr, env)
		# sequencing
		elif keyword == "do":
			for expr in args:
				val = eval(expr, env)
			return val
		# procedure call
		else:
			f = eval(keyword, env)
			xargs = list(eval(arg, env) for arg in args)
			return f(*xargs)

def to_string(exp):
	"""Convert a Python object back into a Lisp-readable string."""
	if isinstance(exp, list):
		return ("[%s]" % ','.join(map(to_string, exp)))
	return str(exp)

def run(program):
	return eval(parse(lex(program)))

def prompt(prompt='mylisp.py> '):
	"""A prompt-read-eval-print loop."""
	while True:
		sys.stdout.write(prompt)
		expr = sys.stdin.readline()
		val = run(expr)
		if val is not None:
			print to_string(val)

if __name__ == "__main__":
	import sys

	if len(sys.argv) == 1:
		prompt()
	else:
		with open(sys.argv[1]) as f:
			print run(f.read())

