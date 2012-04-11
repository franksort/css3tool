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
t_HASH = make_simple('HASH', r'\#{0}'.format(name))
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


blocks = []
selectors = []

### Ya know, stylesheet stuff.  The rest of it.
### Statements, Rules, Rulesets, Declarations, Values

"""
stylesheet  : [ CDO | CDC | S | statement ]*;
statement   : ruleset | at-rule;
at-rule     : ATKEYWORD S* any* [ block | ';' S* ];
block       : '{' S* [ any | block | ATKEYWORD S* | ';' S* ]* '}' S*;
ruleset     : selector? '{' S* declaration? [ ';' S* declaration? ]* '}' S*;
selector    : any+;
declaration : property ':' S* value;
property    : IDENT S*;
value       : [ any | block | ATKEYWORD S* ]+;
any         : [ IDENT | NUMBER | PERCENTAGE | DIMENSION | STRING
              | DELIM | URI | HASH | UNICODE-RANGE | INCLUDES
              | FUNCTION S* any* ')' | DASHMATCH | '(' S* any* ')'
              | '[' S* any* ']' ] S*;
"""

def p_stylesheet(p):
    """stylesheet : CDO
                  | CDC
                  | statements
    """
    p[0] = p[1]
    print 'FOUND STYLESHEET: {0:s}'.format(p[0])

def p_statements(p):
    """statements : statement statements
                  | statement
    """
    p[0] = reduce(lambda x, y: x+y, p[1:])
    print 'FOUND STATEMENTS: {0:s}'.format(p[0])

def p_statement(p):
    """statement : ruleset
    """
    #            | at-rule
    p[0] = p[1]
    print 'FOUND STATEMENT: {0:s}'.format(p[0])


#def p_at_rule(p):
#    """at-rule : ATKEYWORD anys block
#               | ATKEYWORD anys ';'
#    """
#    p[0] = reduce(lambda x, y: x+y, p[1:])
#    print 'FOUND AT RULE: {0:s}'.format(p[0])

#def p_block(p):
#    """block : '{' block_term '}'
#             | '{' '}'
#    """
#    p[0] = reduce(lambda x, y: x+y, p[1:])
#    print 'FOUND BLOCK: {0:s}'.format(p[0])
#    blocks.append(p[0])

#def p_block_term(p):
#    """block_term : any
#                  | block
#                  | ATKEYWORD
#                  | ';'
#    """
#    p[0] = reduce(lambda x, y: x+y, p[1:])
#    print 'FOUND BLOCK TERM: {0:s}'.format(p[0])

def p_ruleset(p):
    """ruleset : selector_group '{' declarations '}'
               | selector_group '{' '}'
               | '{' declarations '}'
               | '{' '}'
    """
    if p[2] == '{':
        selectors.append(p[1])
        blocks.append(p[3])
    p[0] = reduce(lambda x, y: x+y, p[1:])
    print 'FOUND RULESET: {0:s}'.format(p[0])

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



selector_groups = []


### Selectors, Selector Groups, Simple Selector Sequences
###

def p_selector_group(p):
    """selector_group : selector ',' selector_group
                      | selector
    """
    #                 | selector selector_group
    p[0] = reduce(lambda x, y: x+y, p[1:])
    selector_groups.append(p[0])
    print 'FOUND SELECTOR GROUP: {0:s}'.format(p[0])

def p_selector(p):
    """selector : simple_selector_sequence
                | simple_selector_sequence combinator selector
                | simple_selector_sequence selector
    """
    p[0] = reduce(lambda x, y: x+y, p[1:])
    print 'FOUND SELECTOR: {0:s}'.format(p[0])

def p_combinator(p):
    """combinator : '+'
                  | '>'
                  | '~'
    """
    # | S
    p[0] = p[1]
    print 'FOUND COMBINATOR: {0:s}'.format(p[0])

def p_simple_selector_sequence(p):
    """simple_selector_sequence : type_selector sss_types
                                | type_selector
                                | universal_selector sss_types
                                | universal_selector
                                | sss_types
    """
    p[0] = reduce(lambda x, y: x+y, p[1:])
    print 'FOUND SIMPLE SELECTOR SEQUENCE: {0:s}'.format(p[0])

def p_sss_types(p):
    """sss_types : sss_type sss_types
                 | sss_type
    """
    p[0] = reduce(lambda x, y: x+y, p[1:])
    print 'FOUND SIMPLE SELECTOR SEQUENCE TYPES: {0:s}'.format(p[0])

def p_sss_type(p):
    """sss_type : HASH
                | class
                | attrib
                | pseudo
                | negation
    """
    p[0] = p[1]
    print 'FOUND SIMPLE SELECTOR SEQUENCE TYPE: {0:s}'.format(p[0])

def p_type_selector(p):
    """type_selector : namespace_prefix element_name
                     | element_name
    """
    p[0] = reduce(lambda x, y: x+y, p[1:])
    print 'FOUND TYPE SELECTOR: {0:s}'.format(p[0])

def p_universal_selector(p):
    """universal_selector : namespace_prefix '*'
                          | '*'
    """
    p[0] = reduce(lambda x, y: x+y, p[1:])
    print 'FOUND UNIVERSAL SELECTOR: {0:s}'.format(p[0])
    

def p_namespace_prefix(p):
    """namespace_prefix : IDENT '|'
                        | '*' '|'
                        | '|'
    """
    p[0] = reduce(lambda x, y: x+y, p[1:])
    print 'FOUND NAMESPACE PREFIX: {0:s}'.format(p[0])

def p_element_name(p):
    """element_name : IDENT"""
    p[0] = p[1]
    print 'FOUND ELEMENT NAME: {0:s}'.format(p[0])

def p_class(p):
    """class : '.' IDENT"""
    p[0] = p[1] + p[2]
    print 'FOUND CLASS: {0:s}'.format(p[0])


### Pseudo, Expression, Negation
###

def p_pseudo(p):
    """pseudo : ':' ':' IDENT
              | ':' ':' functional_pseudo
              | ':' IDENT
              | ':' functional_pseudo
    """
    p[0] = reduce(lambda x, y: x+y, p[1:])
    print 'FOUND PSEUDO: {0:s}'.format(p[0])

def p_functional_pseudo(p):
    """functional_pseudo : '(' expressions ')'"""
    p[0] = p[1] + p[2] + p[3]
    print 'FOUND PSEUDO FUNCTION: {0:s}'.format(p[0])

def p_expressions(p):
    """expressions : expression expressions
                   | expression
    """
    p[0] = reduce(lambda x, y: x+y, p[1:])
    print 'FOUND EXPRESSIONS: {0:s}'.format(p[0])

def p_expression(p):
    """expression : '+'
                  | '-'
                  | NUMBER
                  | STRING
                  | IDENT
    """
#                 | DIMENSION
    p[0] = p[1]
    print 'FOUND EXPRESSION {0:s}'.format(p[0])

def p_negation(p):
    """negation : ':' NOT '(' negation_arg ')'"""
    p[0] = p[1] + p[2] + p[3] + p[4] + p[5]
    print 'FOUND NEGATION: {0:s}'.format(p[0])

def p_negation_arg(p):
    """negation_arg : type_selector
                    | universal_selector
                    | HASH
                    | class
                    | attrib
                    | pseudo
    """
    p[0] = p[1]
    print 'FOUND NEGATION ARG: {0:s}'.format(p[0])






### Attributes
###

def p_attrib(p):
    """attrib : '[' namespace_prefix IDENT attrib_value ']'
              | '[' namespace_prefix IDENT ']'
              | '[' IDENT attrib_value ']'
              | '[' IDENT ']'
    """
    p[0] = reduce(lambda x, y: x+y, p[1:])
    print 'FOUND ATTRIBUTE: {0:s}'.format(p[0])

def p_attrib_value(p):
    """attrib_value : attrib_selector_op IDENT
                    | attrib_selector_op STRING
    """
    p[0] = p[1] + p[2]
    print 'FOUND ATTRIBUTE VALUE: {0:s}'.format(p[0])

def p_attrib_selector_op(p):
    """attrib_selector_op : PREFIXMATCH
                          | SUFFIXMATCH
                          | SUBSTRINGMATCH
                          | '='
                          | INCLUDES
                          | DASHMATCH
    """
    p[0] = p[1]
    print 'FOUND SELECTOR OP: {0:s}'.format(p[0])

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

f = open('example/style.css')
contents = f.read()
yacc.parse(contents)

html_file = open('example/index.html')
html = html_file.read()
root = fromstring(html)


for s in selectors:
    sel = CSSSelector(s)
    if len(sel(root)) == 0:
        print '{0} NOT FOUND'.format(s)

#for b in blocks:
#    print b

