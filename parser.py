import ply.yacc as yacc
from lexer import CSSLexer
import logging

class CSSParser:

    ######################################
    ### Grammar


    def __init__(self, debug=False):
        self.debug = debug
        self.lexer = CSSLexer(debug=self.debug)
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self, debug=debug, write_tables=0)
        self.selectors = []

    def parse(self, data):
        if data:
            if self.debug:
                self.lexer.debug(data)
            return self.parser.parse(data, self.lexer.lexer)
        else:
            return []

    def p_stylesheet(self, p):
        """stylesheet : CDO
                      | CDC
                      | statements
        """
        p[0] = p[1]
        logging.debug('FOUND STYLESHEET: {0}'.format(p[0]))

    def p_statements(self, p):
        """statements : statement statements
                      | statement
        """
        p[0] = reduce(lambda x, y: x+y, p[1:])
        logging.debug('FOUND STATEMENTS: {0}'.format(p[0]))

    def p_statement(self, p):
        """statement : ruleset
                     | import
                     | namespace
        """
        p[0] = p[1]
        logging.debug('FOUND STATEMENT: {0}'.format(p[0]))


    ##########################################################
    ### Import

    def p_import(self, p):
        """import : IMPORT_SYM STRING import_term ';'
                  | IMPORT_SYM STRING ';'
                  | IMPORT_SYM URI import_term ';'
                  | IMPORT_SYM URI ';'
        """
        p[0] = reduce(lambda x, y: x+y, p[1:])
        logging.debug('FOUND IMPORT: {0}'.format(p[0]))

    def p_import_term(self, p):
        """import_term : IDENT ',' import_term
                       | IDENT
        """
        p[0] = reduce(lambda x, y: x+y, p[1:])
        logging.debug('FOUND IMPORT TERM: {0}'.format(p[0]))


    ##########################################################
    ### Namespace

#namespace
#  : NAMESPACE_SYM S* [namespace_prefix S*]? [STRING|URI] S* ';' S*
#namespace_prefix
#  : IDENT

    def p_namespace(self, p):
        """namespace : NAMESPACE_SYM IDENT STRING ';'
                     | NAMESPACE_SYM IDENT URI ';'
                     | NAMESPACE_SYM STRING ';'
                     | NAMESPACE_SYM URI ';'
        """
        p[0] = reduce(lambda x, y: x+y, p[1:])
        logging.debug('FOUND NAMESPACE: {0}'.format(p[0]))

    ##########################################################
    ### Ruleset

    def p_ruleset(self, p):
        """ruleset : selector_group '{' declarations '}'
                   | selector_group '{' '}'
                   | '{' declarations '}'
                   | '{' '}'
        """
        p[0] = reduce(lambda x, y: x+y, p[1:])
        logging.debug('FOUND RULESET: {0}'.format(p[0]))

    def p_declarations(self, p):
        """declarations : declaration ';' declarations
                        | declaration ';'
                        | declaration
        """
        p[0] = reduce(lambda x, y: x+y, p[1:])
        logging.debug('FOUND DECLARATIONS: {0}'.format(p[0]))

    def p_declaration(self, p):
        """declaration : property ':' values"""
        p[0] = reduce(lambda x, y: x+y, p[1:])
        logging.debug('FOUND DECLARATION: {0}'.format(p[0]))


    def p_property(self, p):
        """property : IDENT"""
        p[0] = p[1]
        logging.debug('FOUND PROPERTY: {0}'.format(p[0]))

    def p_values(self, p):
        """values : value ',' values
                  | value values
                  | value
        """
        p[0] = reduce(lambda x, y: x+y, p[1:])
        logging.debug('FOUND VALUES: {0}'.format(p[0]))

    def p_value(self, p):
        """value : any"""
        #        | block
        #        | ATKEYWORD
        p[0] = p[1]
        logging.debug('FOUND VALUE: {0}'.format(p[0]))

    def p_anys(self, p):
        """anys : any ',' anys
                | any anys
                | any
        """
        p[0] = reduce(lambda x, y: x+y, p[1:])
        logging.debug('FOUND VALUES: {0}'.format(p[0]))

    def p_any(self, p):
        """any : DIMENSION
               | URI
               | PERCENTAGE
               | IDENT
               | STRING
               | NUMBER
               | HASH
               | INCLUDES
               | DASHMATCH
               | FUNCTION anys ')'
               | FUNCTION ')'
               | '(' anys ')'
               | '(' ')'
               | '[' anys ']'
               | '[' ']'
        """
        # UNICODE-RANGE, DELIM
        p[0] = reduce(lambda x, y: x+y, p[1:])
        logging.debug('FOUND ANY: {0}'.format(p[0]))





    ##########################################################
    ### Selectors, Selector Groups, Simple Selector Sequences

    def p_selector_group(self, p):
        """selector_group : selector ',' selector_group
                          | selector
        """
        #                 | selector selector_group
        self.selectors.append(p[1])
        p[0] = reduce(lambda x, y: x+y, p[1:])
        logging.debug('FOUND SELECTOR GROUP: {0}'.format(p[0]))

    def p_selector(self, p):
        """selector : simple_selector_sequence
                    | simple_selector_sequence combinator selector
                    | simple_selector_sequence selector
        """
        p[0] = reduce(lambda x, y: x+' '+y, p[1:])
        logging.debug('FOUND SELECTOR: {0}'.format(p[0]))

    def p_combinator(self, p):
        """combinator : '+'
                      | '>'
                      | '~'
        """
        # | S
        p[0] = p[1]
        logging.debug('FOUND COMBINATOR: {0}'.format(p[0]))

    def p_simple_selector_sequence(self, p):
        """simple_selector_sequence : type_selector sss_types
                                    | type_selector
                                    | universal_selector sss_types
                                    | universal_selector
                                    | sss_types
        """
        p[0] = reduce(lambda x, y: x+y, p[1:])
        logging.debug('FOUND SIMPLE SELECTOR SEQUENCE: {0}'.format(p[0]))

    def p_sss_types(self, p):
        """sss_types : sss_type sss_types
                     | sss_type
        """
        p[0] = reduce(lambda x, y: x+y, p[1:])
        logging.debug('FOUND SIMPLE SELECTOR SEQUENCE TYPES: {0}'.format(p[0]))

    def p_sss_type(self, p):
        """sss_type : HASH
                    | class
                    | attrib
                    | pseudo
                    | negation
        """
        p[0] = p[1]
        logging.debug('FOUND SIMPLE SELECTOR SEQUENCE TYPE: {0}'.format(p[0]))

    def p_type_selector(self, p):
        """type_selector : namespace_prefix element_name
                         | element_name
        """
        p[0] = reduce(lambda x, y: x+y, p[1:])
        logging.debug('FOUND TYPE SELECTOR: {0}'.format(p[0]))

    def p_universal_selector(self, p):
        """universal_selector : namespace_prefix '*'
                              | '*'
        """
        p[0] = reduce(lambda x, y: x+y, p[1:])
        logging.debug('FOUND UNIVERSAL SELECTOR: {0}'.format(p[0]))
        

    def p_namespace_prefix(self, p):
        """namespace_prefix : IDENT '|'
                            | '*' '|'
                            | '|'
        """
        p[0] = reduce(lambda x, y: x+y, p[1:])
        logging.debug('FOUND NAMESPACE PREFIX: {0}'.format(p[0]))

    def p_element_name(self, p):
        """element_name : IDENT"""
        p[0] = p[1]
        logging.debug('FOUND ELEMENT NAME: {0}'.format(p[0]))

    def p_class(self, p):
        """class : '.' IDENT"""
        p[0] = p[1] + p[2]
        logging.debug('FOUND CLASS: {0}'.format(p[0]))


    #######################################################
    ### Pseudo, Expression, Negation

    def p_pseudo(self, p):
        """pseudo : ':' ':' IDENT
                  | ':' ':' functional_pseudo
                  | ':' IDENT
                  | ':' functional_pseudo
        """
        p[0] = reduce(lambda x, y: x+y, p[1:])
        logging.debug('FOUND PSEUDO: {0}'.format(p[0]))

    def p_functional_pseudo(self, p):
        """functional_pseudo : FUNCTION expressions ')'"""
        p[0] = p[1] + p[2] + p[3]
        logging.debug('FOUND PSEUDO FUNCTION: {0}'.format(p[0]))

    def p_expressions(self, p):
        """expressions : expression expressions
                       | expression
        """
        p[0] = reduce(lambda x, y: x+y, p[1:])
        logging.debug('FOUND EXPRESSIONS: {0}'.format(p[0]))

    def p_expression(self, p):
        """expression : '+'
                      | '-'
                      | NUMBER
                      | STRING
                      | IDENT
        """
        #             | DIMENSION
        p[0] = p[1]
        logging.debug('FOUND EXPRESSION {0}'.format(p[0]))

    def p_negation(self, p):
        """negation : ':' NOT negation_arg ')'"""
        p[0] = reduce(lambda x, y: x+y, p[1:])
        logging.debug('FOUND NEGATION: {0}'.format(p[0]))

    def p_negation_arg(self, p):
        """negation_arg : type_selector
                        | universal_selector
                        | HASH
                        | class
                        | attrib
                        | pseudo
        """
        p[0] = p[1]
        logging.debug('FOUND NEGATION ARG: {0}'.format(p[0]))


    ######################################################
    ### Attributes

    def p_attrib(self, p):
        """attrib : '[' namespace_prefix IDENT attrib_value ']'
                  | '[' namespace_prefix IDENT ']'
                  | '[' IDENT attrib_value ']'
                  | '[' IDENT ']'
        """
        p[0] = reduce(lambda x, y: x+y, p[1:])
        logging.debug('FOUND ATTRIBUTE: {0}'.format(p[0]))

    def p_attrib_value(self, p):
        """attrib_value : attrib_selector_op IDENT
                        | attrib_selector_op STRING
        """
        p[0] = p[1] + p[2]
        logging.debug('FOUND ATTRIBUTE VALUE: {0}'.format(p[0]))

    def p_attrib_selector_op(self, p):
        """attrib_selector_op : PREFIXMATCH
                              | SUFFIXMATCH
                              | SUBSTRINGMATCH
                              | '='
                              | INCLUDES
                              | DASHMATCH
        """
        p[0] = p[1]
        logging.debug('FOUND SELECTOR OP: {0}'.format(p[0]))

    def p_error(self, p):
        logging.debug("Syntax error at '{0}'".format(p))
