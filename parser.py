import ply.yacc as yacc
from lexer import CSSLexer

class CSSParser:

    ######################################
    ### Grammar


    def __init__(self):
        self.lexer = CSSLexer()
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self, debug=True)
        self.selectors = []

    def parse(self, data):
        if data:
            return self.parser.parse(data, self.lexer.lexer)
        else:
            return []

    def p_stylesheet(self, p):
        """stylesheet : CDO
                      | CDC
                      | statements
        """
        p[0] = p[1]
        print 'FOUND STYLESHEET: {0:s}'.format(p[0])

    def p_statements(self, p):
        """statements : statement statements
                      | statement
        """
        p[0] = reduce(lambda x, y: x+y, p[1:])
        print 'FOUND STATEMENTS: {0:s}'.format(p[0])

    def p_statement(self, p):
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

    def p_ruleset(self, p):
        """ruleset : selector_group '{' declarations '}'
                   | selector_group '{' '}'
                   | '{' declarations '}'
                   | '{' '}'
        """
        p[0] = reduce(lambda x, y: x+y, p[1:])
        print 'FOUND RULESET: {0:s}'.format(p[0])

    def p_declarations(self, p):
        """declarations : declaration ';' declarations
                        | declaration ';'
                        | declaration
        """
        p[0] = reduce(lambda x, y: x+y, p[1:])
        print 'FOUND DECLARATIONS: {0:s}'.format(p[0])

    def p_declaration(self, p):
        """declaration : property ':' values"""
        p[0] = reduce(lambda x, y: x+y, p[1:])
        print 'FOUND DECLARATION: {0:s}'.format(p[0])


    def p_property(self, p):
        """property : IDENT"""
        p[0] = p[1]
        print 'FOUND PROPERTY: {0:s}'.format(p[0])

    def p_values(self, p):
        """values : value ',' values
                  | value values
                  | value
        """
        p[0] = reduce(lambda x, y: x+y, p[1:])
        print 'FOUND VALUES: {0:s}'.format(p[0])

    def p_value(self, p):
        """value : any"""
        #        | block
        #        | ATKEYWORD
        p[0] = p[1]
        print 'FOUND VALUE: {0:s}'.format(p[0])

    def p_anys(self, p):
        """anys : any ',' anys
                | any anys
                | any
        """
        p[0] = reduce(lambda x, y: x+y, p[1:])
        print 'FOUND VALUES: {0:s}'.format(p[0])

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
        print 'FOUND ANY: {0:s}'.format(p[0]) 





    ##########################################################
    ### Selectors, Selector Groups, Simple Selector Sequences

    def p_selector_group(self, p):
        """selector_group : selector ',' selector_group
                          | selector
        """
        #                 | selector selector_group
        self.selectors.append(p[1])
        p[0] = reduce(lambda x, y: x+y, p[1:])
        print 'FOUND SELECTOR GROUP: {0:s}'.format(p[0])

    def p_selector(self, p):
        """selector : simple_selector_sequence
                    | simple_selector_sequence combinator selector
                    | simple_selector_sequence selector
        """
        p[0] = reduce(lambda x, y: x+' '+y, p[1:])
        print 'FOUND SELECTOR: {0:s}'.format(p[0])

    def p_combinator(self, p):
        """combinator : '+'
                      | '>'
                      | '~'
        """
        # | S
        p[0] = p[1]
        print 'FOUND COMBINATOR: {0:s}'.format(p[0])

    def p_simple_selector_sequence(self, p):
        """simple_selector_sequence : type_selector sss_types
                                    | type_selector
                                    | universal_selector sss_types
                                    | universal_selector
                                    | sss_types
        """
        p[0] = reduce(lambda x, y: x+y, p[1:])
        print 'FOUND SIMPLE SELECTOR SEQUENCE: {0:s}'.format(p[0])

    def p_sss_types(self, p):
        """sss_types : sss_type sss_types
                     | sss_type
        """
        p[0] = reduce(lambda x, y: x+y, p[1:])
        print 'FOUND SIMPLE SELECTOR SEQUENCE TYPES: {0:s}'.format(p[0])

    def p_sss_type(self, p):
        """sss_type : HASH
                    | class
                    | attrib
                    | pseudo
                    | negation
        """
        p[0] = p[1]
        print 'FOUND SIMPLE SELECTOR SEQUENCE TYPE: {0:s}'.format(p[0])

    def p_type_selector(self, p):
        """type_selector : namespace_prefix element_name
                         | element_name
        """
        p[0] = reduce(lambda x, y: x+y, p[1:])
        print 'FOUND TYPE SELECTOR: {0:s}'.format(p[0])

    def p_universal_selector(self, p):
        """universal_selector : namespace_prefix '*'
                              | '*'
        """
        p[0] = reduce(lambda x, y: x+y, p[1:])
        print 'FOUND UNIVERSAL SELECTOR: {0:s}'.format(p[0])
        

    def p_namespace_prefix(self, p):
        """namespace_prefix : IDENT '|'
                            | '*' '|'
                            | '|'
        """
        p[0] = reduce(lambda x, y: x+y, p[1:])
        print 'FOUND NAMESPACE PREFIX: {0:s}'.format(p[0])

    def p_element_name(self, p):
        """element_name : IDENT"""
        p[0] = p[1]
        print 'FOUND ELEMENT NAME: {0:s}'.format(p[0])

    def p_class(self, p):
        """class : '.' IDENT"""
        p[0] = p[1] + p[2]
        print 'FOUND CLASS: {0:s}'.format(p[0])


    #######################################################
    ### Pseudo, Expression, Negation

    def p_pseudo(self, p):
        """pseudo : ':' ':' IDENT
                  | ':' ':' functional_pseudo
                  | ':' IDENT
                  | ':' functional_pseudo
        """
        p[0] = reduce(lambda x, y: x+y, p[1:])
        print 'FOUND PSEUDO: {0:s}'.format(p[0])

    def p_functional_pseudo(self, p):
        """functional_pseudo : '(' expressions ')'"""
        p[0] = p[1] + p[2] + p[3]
        print 'FOUND PSEUDO FUNCTION: {0:s}'.format(p[0])

    def p_expressions(self, p):
        """expressions : expression expressions
                       | expression
        """
        p[0] = reduce(lambda x, y: x+y, p[1:])
        print 'FOUND EXPRESSIONS: {0:s}'.format(p[0])

    def p_expression(self, p):
        """expression : '+'
                      | '-'
                      | NUMBER
                      | STRING
                      | IDENT
        """
    #                 | DIMENSION
        p[0] = p[1]
        print 'FOUND EXPRESSION {0:s}'.format(p[0])

    def p_negation(self, p):
        """negation : ':' NOT '(' negation_arg ')'"""
        p[0] = reduce(lambda x, y: x+y, p[1:])
        print 'FOUND NEGATION: {0:s}'.format(p[0])

    def p_negation_arg(self, p):
        """negation_arg : type_selector
                        | universal_selector
                        | HASH
                        | class
                        | attrib
                        | pseudo
        """
        p[0] = p[1]
        print 'FOUND NEGATION ARG: {0}'.format(p[0])


    ######################################################
    ### Attributes

    def p_attrib(self, p):
        """attrib : '[' namespace_prefix IDENT attrib_value ']'
                  | '[' namespace_prefix IDENT ']'
                  | '[' IDENT attrib_value ']'
                  | '[' IDENT ']'
        """
        p[0] = reduce(lambda x, y: x+y, p[1:])
        print 'FOUND ATTRIBUTE: {0}'.format(p[0])

    def p_attrib_value(self, p):
        """attrib_value : attrib_selector_op IDENT
                        | attrib_selector_op STRING
        """
        p[0] = p[1] + p[2]
        print 'FOUND ATTRIBUTE VALUE: {0}'.format(p[0])

    def p_attrib_selector_op(self, p):
        """attrib_selector_op : PREFIXMATCH
                              | SUFFIXMATCH
                              | SUBSTRINGMATCH
                              | '='
                              | INCLUDES
                              | DASHMATCH
        """
        p[0] = p[1]
        print 'FOUND SELECTOR OP: {0}'.format(p[0])

    def p_error(self, p):
        print "Syntax error at '{0}'".format(p)
