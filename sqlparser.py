# -----------------------------------------------------------------------------
# sqlparser.py
#
# parser of select statement
# -----------------------------------------------------------------------------
# reserved words
reserved = {
   'select' : 'SELECT',
   'for' : 'FOR',
   'by' : 'BY',
   'temperature' : 'TEMPERATURE',
   'humidity' : 'HUMIDITY',
   'brightness' : 'BRIGHTNESS',
   'battery' : 'BATTERY',
   'where' : 'WHERE',
   'and' : 'AND',
}
# List of token names. 
tokens = [
    'TIMES',
    'LESS','GREATER','EQUALS',
    'LESSEQUALS','GREATEREQUALS',
    'LPAREN','RPAREN',
    'NUMBER','ID'
] + list(reserved.values())
# Regular expression rules for simple tokens

t_TIMES   = r'\*'
t_LESS  = r'<'
t_GREATER = r'>'
t_EQUALS  = r'='
t_LESSEQUALS = r'<='
t_GREATEREQUALS = r'>='
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
# regular expression rules with some action code
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)    
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'ID')    # Check for reserved words
    return t
# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule when illegal characters are detected
def t_error(t):
    print "Illegal character '%s'" % t.value[0]   # the rest of the input string that has not been tokenized
    t.lexer.skip(1)
# Build the lexer
import ply.lex as lex
lexer = lex.lex()
# Test it output
#lexer.input('select temperature , brightness for nb=50 by t=60 where temperature >= 20')
#while True:
 #   tok = lexer.token()
  #  if not tok: break
   # print tok

#---------------------------------------------------------------------------------------------------------------

def p_query_select(p):
	'statement : SELECT select_list FOR NUMBER BY NUMBER WHERE condition'
	p[0] ="Q"+" "+str(p[4])+" "+str(p[6])+"/"+str(len(p[2].split(" ")))+" "+p[2]+"|"+p[8]
	print(p[0])
        return(p[0])
def p_query_select_without_where(p):
	'statement : SELECT select_list FOR NUMBER BY NUMBER'
	p[0] ="Q"+" "+str(p[4])+" "+str(p[6])+"/"+str(len(p[2].split(" ")))+" "+p[2]+"|"+"null"
	print(p[0])
def p_select_list(p):
    'select_list : select_list  select_item'
    p[0] = p[1]+" "+p[2]
          
def p_select_list_arg(p):
	 '''select_list : select_item
	                | TIMES '''
	 p[0]=p[1]
	 
def p_select_item(p):
    '''select_item :  TEMPERATURE
                   |  BRIGHTNESS
                   |  HUMIDITY
                   |  BATTERY '''
    if p[1] == 'temperature'  : p[0] = '1'
    elif p[1] == 'humidity': p[0] = '2'
    elif p[1] == 'brightness': p[0] = '3'
    elif p[1] == 'battery': p[0] = '4'
    #p[0]=p[1]
def p_where_condition(p):
	'condition : condition AND condition'
	p[0]=p[1]+" "+p[3]
	
def p_where_condition_item(p):
    'condition : select_item op NUMBER'
    p[0] = p[1]+p[2]+str(p[3])
    	
def p_operator(p):
    '''op : LESS
          | GREATER
          | EQUALS
          | LESSEQUALS
          | GREATEREQUALS'''
    if p[1] == '<'  : p[0] = 'LS'
    elif p[1] == '>': p[0] = 'GR'
    elif p[1] == '=': p[0] = 'EQ'
    elif p[1] == '<=': p[0] = 'LE'
    elif p[1] == '>=': p[0] = 'GE'
    #p[0] = p[1]           

def p_error(p):
    print("Syntax error at '%s'" % p.value)
import ply.yacc as yacc
yacc.yacc()

#while True:
 #   try:
  #      s = raw_input('select statement > ')   
   # except EOFError:
    #    break
    #yacc.parse(s)
#Q nb1 nb2/nbattribut 1 2 3 |1/2/3GE20
