import operator as op
from functools import reduce

Symbol = str              # A Scheme Symbol is implemented as a Python str
Number = (int, float)     # A Scheme Number is implemented as a Python int or float
Atom   = (Symbol, Number) # A Scheme Atom is a Symbol or Number
List   = list             # A Scheme List is implemented as a Python list
Exp    = (Atom, List)     # A Scheme expression is an Atom or List
Env    = dict             # A Scheme environment (defined below)
                          # is a mapping of {variable: value}


def tokenize(chars: str):
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()

def read_from_tokens(tokens: list) -> Exp:
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF')
    token = tokens.pop(0)
    if token == '(':
        L = []
        while tokens[0] != ')':
            L.append(read_from_tokens(tokens))
        tokens.pop(0)  # pop off ')'
        return L
    elif token == ')':
        raise SyntaxError('unexpected )')
    else:
        return atom(token)

def atom(token: str):
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return Symbol(token)

def deep_tuple(l):
    r = []
    if isinstance(l, list):
        for i in l:
            r.append(deep_tuple(i))
    else:
        return l
    return tuple(r)

def translate(s):
    return deep_tuple(read_from_tokens(tokenize(s)))



def decode(r):
    r = r.decode().strip("\n")
    if r == "#t":
        r = True
    elif r == "#f":
        r = False
    else:
        r = int(r)
    return r



def multi_args_f(f):
    def inner(*args):
        return reduce(f, args)
    return inner

builtins = {
    '+': multi_args_f(op.add),
    '-': op.sub,
    '*': op.mul,
    '/': op.truediv,
    '>': op.gt,
    '<': op.lt,
    '>=': op.ge,
    '<=': op.le,
    '=': op.eq,
    'abs': abs,
    'append': op.add,
    'begin': lambda *x: x[-1],
    'car': lambda x: x[0],
    'cdr': lambda x: x[1:],
    'cons': lambda x, y: [x] + y,
    'eq?': op.is_,
    'equal?': op.eq,
    'length': len,
    'list': lambda *x: list(x),
    'list?': lambda x: isinstance(x, list),
    'map': map,
    'max': max,
    'min': min,
    'not': op.not_,
    'null?': lambda x: x == [],
    'number?': lambda x: isinstance(x, Number),
    'procedure?': callable,
    'round': round,
    'symbol?': lambda x: isinstance(x, Symbol),
    '#t': True,
    '#f': False,
    }