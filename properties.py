import ply.lex as lex
import ply.yacc as yacc
import re
from lxml.cssselect import CSSSelector
from lxml.html import fromstring

###############################
# Lex                         #
###############################

"""

Ply compiles a master regex from the tokens specified.  When specified with
strings, they are sorted by descending length.  When specified with functions,
they are added in the order they are defined.

With this in mind, I have decided to specify all tokens with functions.  Ply
uses the function's docstring as the regex.

"""


### Regex Helpers
###

nonascii  = r'([^\0-\177])'
unicode   = r'(\\[0-9a-f]{1,6}(\r\n|[ \n\r\t\f])?)'
escape    = r'({0}|\\[^\n\r\f0-9a-f])'.format(unicode)

w         = r'[ \t\r\n\f]*'
nl        = r'\n|\r\n|\r|\f'

invalid2  = r"\'([^\n\r\f\\']|\\{0}|{1}|{2})*".format(nl, nonascii, escape)
invalid1  = r'\"([^\n\r\f\\"]|\\{0}|{1}|{2})*'.format(nl, nonascii, escape)
invalid   = r'{invalid1}|{invalid2}'

string2   = r"(\'([^\n\r\f\\']|\\{0}|{1}|{2})*\')".format(nl, nonascii, escape)
string1   = r'(\"([^\n\r\f\\"]|\\{0}|{1}|{2})*\")'.format(nl, nonascii, escape)
string    = r'{0}|{1}'.format(string1, string2)

nmstart   = r'([_a-z]|{0}|{1})'.format(nonascii, escape)
nmchar    = r'([_a-z0-9-]|{0}|{1})'.format(nonascii, escape)
ident     = r'[-]?{0}{1}*'.format(nmstart, nmchar)
name      = r'{0}+'.format(nmchar)

url       = r'([!#$%&*-~]|{0}|{1})+'.format(nonascii, escape)
num       = r'([+-]?[0-9]+|[0-9]*\.[0-9]+)'

literals = ['|', '*', '[', ']', '=', '+', '>',
            '~', '.', ',', '-', ':',
            '{', '}', ',', ';', '(', ')']

tokens = []

### Whitespace
###

#tokens.append('S')
#def t_S(t): return t
#t_S.__doc__ = r'[ \t\r\n\f]+'

def make_simple(name, pattern):
    global tokens
    def func(t):
        return t
    tokens.append(name)
    func.__name__ = 't_%s' % name
    func.__doc__ = pattern
    return func

def make_unit(name, unit):
    global tokens
    def func(t):
        return t
    tokens.append(name)
    func.__name__ = 't_%s' % name
    func.__doc__ = '%s%s' % (num, unit)
    return func



### Attribute/Value Selectors
###


t_INCLUDES = make_simple('INCLUDES', r'\~=')
t_DASHMATCH = make_simple('DASHMATCH', r'\|=')
t_PREFIXMATCH = make_simple('PREFIXMATCH', r'\^=')
t_SUFFIXMATCH = make_simple('SUFFIXMATCH', r'\$=')
t_SUBSTRINGMATCH = make_simple('SUBSTRINGMATCH', r'\*=')

### Lengths
###

t_EM = make_unit('EM', 'em')
t_EX = make_unit('EX', 'ex')
t_PIXEL = make_unit('PIXEL', 'px')
t_CENTIMETER = make_unit('CENTIMETER', 'cm')
t_MILLIMETER = make_unit('MILLIMETER', 'mm')
t_INCH = make_unit('INCH', 'in')
t_POINT = make_unit('POINT', 'pt')
t_PC = make_unit('PC', 'pc')


### Angles
###

t_DEGREE = make_unit('DEGREE', 'deg')
t_RADIAN = make_unit('RADIAN', 'rad')
t_GRADIAN = make_unit('GRADIAN', 'grad')

### Time
###

t_MILLISECOND = make_unit('MILLISECOND', 'ms')
t_SECOND = make_unit('SECOND', 's')

### Frequency
###

t_HERTZ = make_unit('HERTZ', 'Hz')
t_KILOHERTZ = make_unit('KILOHERTZ', 'kHz')


### Others
###

t_NOT = make_simple('NOT', r'not\(')
t_URI = make_simple('URI', r'url\(({0}|{1})\)'.format(string, url))
t_FUNCTION = make_simple('FUNCTION', r'{0}\('.format(ident))
<<<<<<< HEAD
t_HASH = make_simple('HASH', r'\#{0}'.format(name))
=======
t_HASH= make_simple('HASH', r'\#{0}'.format(name))
>>>>>>> 69d455ace194922c00ea0e711c5fffbffb984d8e
t_DIMENSION = make_simple('DIMENSION', r'{0}{1}'.format(num, ident))
t_PERCENTAGE = make_simple('PERCENTAGE', r'{0}\%'.format(num))

### Comments
###

t_CDO = make_simple('CDO', r'<!--')
t_CDC = make_simple('CDC', r'-->')


### Basic
###


t_NUMBER = make_simple('NUMBER', r'{0}'.format(num))
t_STRING = make_simple('STRING', r'{0}'.format(string))
t_IDENT = make_simple('IDENT', r'{0}'.format(ident))


t_ignore = ' \t\r\n\f'
t_ignore_COMMENT = r'\/\*[^*]*\*+([^/*][^*]*\*+)*\/'

def t_error(t):
    print "Illegal character '{0:s}'".format(t.value[0])
    t.lexer.skip(1)

lex.lex(reflags=re.IGNORECASE, debug=1)


f = open('example/style.css')
contents = f.read()
lex.input(contents)
#lex.input('url(imgs/face01.gif)')
while True:
    tok = lex.token()
    if not tok: break
    print tok




###############################
# Yacc                        #
###############################


def p_declarations(p):
    """declarations : declaration ';' declarations
                    | declaration ';'
                    | declaration
    """
    p[0] = reduce(lambda x, y: x+y, p[1:])
    print 'FOUND DECLARATIONS: {0:s}'.format(p[0])

def p_declaration(p):
    """declaration : property ':' values"""
    p[0] = p[1] + p[2] + p[3]
    print 'FOUND DECLARATION: {0:s}'.format(p[0])

def p_property(p):
    """property : IDENT"""
    p[0] = p[1]
    print 'FOUND PROPERTY: {0:s}'.format(p[0])

def p_values(p):
    """values : value ',' values
              | value values
              | value
    """
    p[0] = reduce(lambda x, y: x+y, p[1:])
    print 'FOUND VALUES: {0:s}'.format(p[0])

def p_value(p):
    """value : any
    """
    #        | block
    #        | ATKEYWORD
    p[0] = p[1]
    print 'FOUND VALUE: {0:s}'.format(p[0])

def p_anys(p):
    """anys : any anys
            | any
    """
    p[0] = reduce(lambda x, y: x+y, p[1:])
    print 'FOUND VALUES: {0:s}'.format(p[0])

def p_any(p):
    """any : EM
           | EX
           | PIXEL
           | CENTIMETER
           | MILLIMETER
           | INCH
           | POINT
           | PC
           | DEGREE
           | RADIAN
           | GRADIAN
           | MILLISECOND
           | SECOND
           | HERTZ
           | KILOHERTZ
           | URI
           | PERCENTAGE
           | IDENT
           | STRING
           | NUMBER
           | DIMENSION
           | HASH
           | INCLUDES
           | DASHMATCH
           | IDENT '(' anys ')'
           | IDENT '(' ')'
           | '(' anys ')'
           | '(' ')'
           | '[' anys ']'
           | '[' ']'
    """
    # UNICODE-RANGE, DELIM, URI
    p[0] = reduce(lambda x, y: x+y, p[1:])
    print 'FOUND ANY: {0:s}'.format(p[0]) 


def p_error(p):
    print "Syntax error at '%r'" % p

yacc.yacc()

"""
while 1:
    try:
        s = raw_input('calc > ')
    except EOFError:
        break
    if not s: continue
    yacc.parse(s)
"""

f = open('example/properties.txt')
contents = f.read()
yacc.parse(contents)
