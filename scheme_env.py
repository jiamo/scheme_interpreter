import math
import operator as op
from util import *
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
            # translate let to lambda
            names = [b[0] for b in sexp[1]]
            values = [b[1] for b in sexp[1]]
            return seval((('lambda', tuple(names), ('begin', ) + sexp[2:]), *values), environ)

        if sexp[0] == 'lambda':

            def procedure(*args):      # *args accepts any number of args
                argnames = sexp[1]
                body = sexp[2]
                newenviron = { }
                # Must bind the argument names to argument values in the new environ
                for n in range(len(argnames)):
                    newenviron[argnames[n]] = args[n]
                return seval(body, environ + (newenviron,))
            return procedure


        proc = seval(sexp[0], environ)
        args = [ ]
        for arg in sexp[1:]:
            args.append(seval(arg, environ))
        return proc(*args)


if __name__ == "__main__":
    # run file
    import sys
    env =  (builtins, {})
    with open(sys.argv[1], "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("#") or line.startswith(";") or line.startswith("(require"):
                continue
            x = translate(line)
            print(x)
            r1 = seval(x, env)
        
    print(r1)