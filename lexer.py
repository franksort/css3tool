import ply.lex as lex
import re
import logging

class CSSLexer:
    """
    This is where tokens are made, compliments of ply.lex.

    Ply compiles a master regex from the tokens specified below.  When tokens
    are specified using strings (ie. t_DIGIT = r'\d'), the regex rules are
    sorted by descending length and added to the master regex.  When
    specified with functions, the rules are added in the order they are
    defined below.

    To ensure the token regexes are being added to the master regex in a
    predictable order, I have decided to specify all tokens using functions.
    """

    ############################################################
    ### Regex Helpers

    nonascii  = r'([^\0-\177])'
    unicode = r'(\\[0-9a-f]{1,6}(\r\n|[ \n\r\t\f])?)'
    escape = r'({0}|\\[^\n\r\f0-9a-f])'.format(unicode)

    w = r'[ \t\r\n\f]*'
    nl = r'\n|\r\n|\r|\f'

    invalid2 = r"\'([^\n\r\f\\']|\\{0}|{1}|{2})*".format(nl, nonascii, escape)
    invalid1 = r'\"([^\n\r\f\\"]|\\{0}|{1}|{2})*'.format(nl, nonascii, escape)
    invalid = r'{invalid1}|{invalid2}'

    string2 = r"(\'([^\n\r\f\\']|\\{0}|{1}|{2})*\')".format(nl, nonascii, escape)
    string1 = r'(\"([^\n\r\f\\"]|\\{0}|{1}|{2})*\")'.format(nl, nonascii, escape)
    string = r'{0}|{1}'.format(string1, string2)

    nmstart = r'([_a-z]|{0}|{1})'.format(nonascii, escape)
    nmchar = r'([_a-z0-9-]|{0}|{1})'.format(nonascii, escape)
    ident = r'[-]?{0}{1}*'.format(nmstart, nmchar)
    name = r'{0}+'.format(nmchar)

    url = r'([!#$%&*-~]|{0}|{1})+'.format(nonascii, escape)
    num = r'([+-]?[0-9]+|[0-9]*\.[0-9]+)'

    def __init__(self, debug=False):
        self.lexer = lex.lex(module=self, reflags=re.IGNORECASE, debug=debug)

    ############################################################
    #################### Token Definitions #####################
    ############################################################


    literals = ['|', '*', '[', ']', '=', '+', '>', '~',
                '.', ',', '-', ':', '{', '}', ',', ';', '(', ')']
    tokens = []


    ############################################################
    ### Attribute/Value Selectors

    tokens.append('INCLUDES')
    def t_INCLUDES(self, t):
        r'\~='
        return t

    tokens.append('DASHMATCH')
    def t_DASHMATCH(self, t):
        r'\|='
        return t

    tokens.append('PREFIXMATCH')
    def t_PREFIXMATCH(self, t):
        r'\^='
        return t

    tokens.append('SUFFIXMATCH')
    def t_SUFFIXMATCH(self, t):
        r'\$='
        return t

    tokens.append('SUBSTRINGMATCH')
    def t_SUBSTRINGMATCH(self, t):
        r'\*='
        return t


    ############################################################
    ### Dimensions

    tokens.append('DIMENSION')
    def t_DIMENSION(self, t): return t
    t_DIMENSION.__doc__ = r'{0}{1}'.format(num, ident)


    ############################################################
    ### Functions

    tokens.append('NOT')
    def t_NOT(self, t): return t
    t_NOT.__doc__ = r'not\('

    tokens.append('URI')
    def t_URI(self, t): return t
    t_URI.__doc__ = r'url\(({0}|{1})\)'.format(string, url)

    tokens.append('FUNCTION')
    def t_FUNCTION(self, t): return t
    t_FUNCTION.__doc__ = r'{0}\('.format(ident)


    ############################################################
    ### Misc.

    tokens.append('HASH')
    def t_HASH(self, t): return t
    t_HASH.__doc__ = r'\#{0}'.format(name)

    tokens.append('PERCENTAGE')
    def t_PERCENTAGE(self, t): return t
    t_PERCENTAGE.__doc__ = r'{0}\%'.format(num)


    ############################################################
    ### At-keywords

    tokens.append('IMPORT_SYM')
    def t_IMPORT_SYM(self, t):
        r'\@import'
        return t

    tokens.append('NAMESPACE_SYM')
    def t_NAMESPACE_SYM(self, t):
        r'\@namespace'
        return t

    tokens.append('ATKEYWORD')
    def t_ATKEYWORD(self, t): return t
    t_ATKEYWORD.__doc__ = r'\@{0}'.format(name)




    ############################################################
    ### Comments

    tokens.append('CDO')
    def t_CDO(self, t):
        r'<!--'
        return t

    tokens.append('CDC')
    def t_CDC(self, t):
        r'-->'
        return t


    ############################################################
    ### Primitive

    tokens.append('NUMBER')
    def t_NUMBER(self, t): return t
    t_NUMBER.__doc__ = r'{0}'.format(num)

    tokens.append('STRING')
    def t_STRING(self, t): return t
    t_STRING.__doc__ = r'{0}'.format(string)

    tokens.append('IDENT')
    def t_IDENT(self, t): return t
    t_IDENT.__doc__ = r'{0}'.format(ident)

    t_ignore = ' \t\r\n\f'
    t_ignore_COMMENT = r'\/\*[^*]*\*+([^/*][^*]*\*+)*\/'


    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        print "Illegal character '{0}'".format(t.value[0])
        t.lexer.skip(1)
    
    def debug(self, data):
        self.lexer.input(data)
        while True:
             tok = self.lexer.token()
             if not tok: break
             logging.debug(tok)
