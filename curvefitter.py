from scipy.optimize import curve_fit
import re

class CurveFitter:

    def __init__(self):
        self.xdata = None
        self.ydata = None
        self.func = None
        self.nparam = None
        self.varnames = None
        self.p0 = None

    def set_data(self, xdata, ydata):

        if len(xdata) != len(ydata):
            raise ValueError(" ")

        self.xdata = xdata
        self.ydata = ydata

    def set_func(self, func):
        if not hasattr(func, '__call__'):
            raise TypeError('Should be a function')

        self.nparam = func.func_code.co_argcount - 1
        if self.nparam < 1:
            raise ValueError('The function should have at least one parameter to fit')

        self.func = func
        # variable names, we do not care about the first one (x-variable)
        self.varnames = list(func.func_code.co_varnames)[1:]

    def set_p0(self, p0):

        if self.func is None:
            raise AttributeError('The function should first be set')

        if len(p0) != self.nparam:
            raise ValueError('The number of initial values is not equal to the number of parameters')

        self.p0 = p0

    def fit(self):

        if None in (self.xdata, self.ydata, self.func):
            raise ValueError('Not all requirements are set')

        popt, pcov = curve_fit(self.func, self.xdata, self.ydata, self.p0)
        popt_dict = dict(zip(self.varnames, popt))

        return popt_dict

def parse(equation):
    from pyparsing import Word, Literal, CaselessLiteral, Combine 
    from pyparsing import Optional, Forward, ZeroOrMore, StringEnd
    from pyparsing import nums, alphas, alphanums

    # grammar of equation
    point = Literal('.')
    e = CaselessLiteral('E')
    plusorminus = Literal('+') | Literal('-')
    number = Word(nums)
    integer = Combine(Optional(plusorminus) + number)
    floatnumber = Combine(integer + Optional(point + Optional(number)) +
                          Optional(e + integer))
    ident = Word(alphas, alphanums + '_')
    plus = Literal('+')
    minus = Literal('-')
    mult = Literal('*')
    div = Literal('/')
    expop = Literal('^')
    lpar = Literal('(').suppress()
    rpar = Literal(')').suppress()
    addop = plus | minus
    multop = mult | div
    # functions
    sin = Literal('sin')
    cos = Literal('cos')
    exp = Literal('exp')
    ln = Literal('ln')
    log = Literal('log')
    functions = sin | cos | exp | ln | log

    expr = Forward()
    atom = (functions + lpar + expr + rpar)|\
           (e | floatnumber | integer | ident) |\
           (lpar + expr + rpar)

    factor = Forward()
    factor << atom + ZeroOrMore(expop + factor)

    term = factor + ZeroOrMore(multop + factor)
    expr << term + ZeroOrMore(addop + term)
    pattern = expr + StringEnd()

    variables = []
    l = pattern.parseString(equation)

    functions = ('sin', 'cos', 'exp', 'ln', 'log')
    for op in l:
        if re.search('^[a-zA-Z][a-zA-Z0-9_]*$', op):
            if op not in functions:
                variables.append(op)
    variables = set(variables)

    from keyword import iskeyword
    for var in variables:
        if iskeyword(var):
            raise ValueError('You are using one of the forbidden words, ASSHOLE')
        
    return variables


def string_to_func(expression, parameters, xvariable):

    expression = expression.replace('^', '**')

    # make a proper python function definition 
    func_string = "def myfunc(" + xvariable
    for parameter in parameters:
        func_string += ', '
        func_string += parameter
    func_string += '):\n'
    func_string += '    from numpy import log as ln, log10 as log, sin, cos, exp\n'
    func_string += '    return ' + expression

    # build the code object and execute it
    exec(compile(func_string, 'myfunc.py', 'exec'))

    return myfunc

def main():

    # input data 
    xdata = [1, 2, 3, 4, 5,]
    ydata = [1.9, 8.2, 18.9, 32.5, 50]
    expression = 'a*x^2'
    xvariable = 'x'
    #=============================

    parameters = parse(expression)

    if xvariable not in parameters:
        raise ValueError('There is no x-variable in your expression')
    else:
        parameters.remove(xvariable)

    my_func = string_to_func(expression, parameters, xvariable)

    cf = CurveFitter()
    cf.set_data(xdata, ydata)
    cf.set_func(my_func)
    popt = cf.fit()
    print popt

    #y_fit_data = [my_func(x, popt[0]) for x in xdata]

    #fig = plt.figure()
    #axes = fig.add_subplot(111)
    #axes.scatter(xdata, ydata)
    #axes.plot(xdata, y_fit_data)
    #plt.show()

if __name__=='__main__':
    main()
