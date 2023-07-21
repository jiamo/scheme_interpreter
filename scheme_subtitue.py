import math
import operator as op

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


from functools import reduce
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

env = { }

def clean_env():
    global env
    env = {}

def isprimitive(sexp):
    return isinstance(sexp, int) or isinstance(sexp, float)

def substitute(sexp, name, value):
    if sexp == name:
        return value
    elif isinstance(sexp, tuple):
        result = [ ]
        for item in sexp:
            result.append(substitute(item, name, value))
        return tuple(result)
    else:
        return sexp


def seval(sexp):
    if isprimitive(sexp):
        return sexp
    # builtins
    if isinstance(sexp, str) and sexp in env:
        return env[sexp]
    if isinstance(sexp, str) and sexp in builtins:
        return builtins[sexp]

    if isinstance(sexp, str):
        return sexp

    if isinstance(sexp, tuple):
        if sexp[0] == 'define':
            name = sexp[1]
            value = seval(sexp[2])
            env[name] = value
            return None

        if sexp[0] == 'set!':
            name = sexp[1]
            value = seval(sexp[2])
            # Go Find the previous definition and change it
            env[name] = value
            return None

        if sexp[0] == 'if':
            test = seval(sexp[1])
            if test:
                return seval(sexp[2])
            else:
                return seval(sexp[3])
        if sexp[0] == 'cond':
            for exp in sexp[1:]:
                test_expr = exp[0]
                if test_expr == 'else' or seval(test_expr):
                    return seval(exp[1])
                else:
                    continue
        if sexp[0] == 'begin':
            for e in sexp[1:]:
                r = seval(e)
            return r
        if sexp[0] == 'let':
            names = [b[0] for b in sexp[1]]
            values = [b[1] for b in sexp[1]]

            for exp in sexp[2:]:
                for name, value in zip(names, values):
                    exp = substitute(exp, name, value)
                r = seval(exp)
            return r

        if sexp[0] == 'lambda':
            def procedure(*args):
                argnames = sexp[1]
                body = sexp[2]
                for n in range(len(argnames)):
                    body = substitute(body, argnames[n], args[n])
                return seval(body)

            return procedure

        proc = seval(sexp[0])
        args = []
        for arg in sexp[1:]:
            args.append(seval(arg))
        # print(f"{proc=}")
        return proc(*args)



if __name__ == "__main__":
    # run file
    import sys
    with open(sys.argv[1], "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("#") or line.startswith(";") or line.startswith("(require"):
                continue
            r1 = seval(translate(line))
        
    print(r1)