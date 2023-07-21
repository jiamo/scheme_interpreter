import math
import operator as op
fact = ('define', 'fact',
        ('lambda', ('n',), ('if', ('=', 'n', 1),
                            1,
                            ('*', 'n', ('fact', ('-', 'n', 1))))))


Symbol = str              # A Scheme Symbol is implemented as a Python str
Number = (int, float)     # A Scheme Number is implemented as a Python int or float
Atom   = (Symbol, Number) # A Scheme Atom is a Symbol or Number
List   = list             # A Scheme List is implemented as a Python list
Exp    = (Atom, List)     # A Scheme expression is an Atom or List
Env    = dict             # A Scheme environment (defined below)
                          # is a mapping of {variable: value}
s = "(define fact (lambda (n) (if (= n 1) 1 (* n (fact (- n 1))))))"
s1 = "((lambda (n) (if (= n 1) 1 (* n (fact (- n 1))))) 5)"


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

# Checking for primitive datatypes (like ints)
def isprimitive(sexp):
    return isinstance(sexp, int) or isinstance(sexp, float)

def seval(sexp, environ):
    # Primitives.  Integers, floats, etc.  Just exist.
    if isprimitive(sexp):
        return sexp
    # There are some "builtins" and they have names (+, -, *, /, etc.)
    # There are also user-define names (define)
    # Modify to look at nested environments
    if isinstance(sexp, str):
        for env in reversed(environ):
            if sexp in env:
                return env[sexp]
        raise NameError(f'{sexp} not defined')

    # There are procedures (procedure application)
    if isinstance(sexp, tuple):
        # ('define', 'x', 42)
        if sexp[0] == 'define':      # "Special Form"
            name = sexp[1]
            value = seval(sexp[2], environ)
            # Always store in the most local environment
            environ[-1][name] = value
            return None

        if sexp[0] == 'set!':
            name = sexp[1]
            value = seval(sexp[2], environ)
            # Go Find the previous definition and change it
            for env in reversed(environ):
                if name in env:
                    env[name] = value
                    break
            else:
                raise NameError(f'{name} not defined')
            return None

        if sexp[0] == 'if':
            test = seval(sexp[1], environ)     # Evaluate the condition
            if test:                  # Only one branch evaluates
                return seval(sexp[2], environ)
            else:
                return seval(sexp[3], environ)
        if  sexp[0] == 'cond':
            for exp in sexp[1:]:
                test_expr = exp[0]
                if test_expr == 'else' or seval(test_expr, environ):
                    return seval(exp[1], environ)
                else:
                    continue

        if sexp[0] == 'begin':
            for exp in sexp[1:]:
                result = seval(exp, environ)
            return result
        if sexp[0] == 'let':
            # print(sexp)
            # name = sexp[1][0][0]
            # value = seval(sexp[1][0][1], environ)
            # new_environ = {name: value}
            # for exp in sexp[2:]:
            #     r = seval(exp, environ + (new_environ, ))
            # return r

            names = [b[0] for b in sexp[1]]
            values = [b[1] for b in sexp[1]]
            print( sexp[2:])
            return seval((('lambda', tuple(names), ('begin', ) + sexp[2:]), *values), environ)

        if sexp[0] == 'lambda':
            # ('lambda', ('x', 'y'), ('+', 'x', 'y'))
            #            ^^^ args    ^^^^ body
            # Create a procedure
            def procedure(*args):      # *args accepts any number of args
                # How do procedures work?
                # Substitution!
                # Each argument name gets substituted by an argument value
                #   "x" -> 13
                argnames = sexp[1]
                body = sexp[2]
                newenviron = { }
                # Must bind the argument names to argument values in the new environ
                for n in range(len(argnames)):
                    newenviron[argnames[n]] = args[n]
                # Execute body in current definition environment + new environ
                return seval(body, environ + (newenviron,))
            return procedure

        # ('+', 2, 3)
        # How does a procedure call evaluate?
        # 1. Look up the procedure.
        proc = seval(sexp[0], environ)

        # 2. Evaluate the procedure arguments.  Applicative order.
        #    (Arguments evaluated before the procedure)
        args = [ ]
        for arg in sexp[1:]:
            args.append(seval(arg, environ))

        # 3. Execute the procedure.
        return proc(*args)