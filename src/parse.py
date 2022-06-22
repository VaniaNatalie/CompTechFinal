
from token import Token

# Storing declared variables
var = []
func = []
funcParams = []

# Parser
class Parse:   
    def __init__ (self, s):
        # string input
        self.s = s 
        # token object
        self.t = Token(self.s)

    
    # Main entry point
    def parsee(self):     
        # checker for blocks
        self.blockChecker = 0
        # block checker flag 
        self.lookahead = self.t.getNextToken('parse')
        return self.program()

    def program(self):
        ast = {
            'type': 'Program',
            'body': self.statementList()
        }
        return ast
    
    def statementList(self, blockStatementStopper = None):
        # If it is one statement
        statementList = []
        self.flag = False
        
        if self.lookahead.get('type') != 'block':
            statementList = [self.statement()]
        
        # If checking for block statement
        if blockStatementStopper != None:
            self.prevTempBlockChecker = 0
            # While not reached end of file and there is indentation
            while (self.lookahead != None and self.lookahead.get('type') == blockStatementStopper) \
                or self.flag == True:

                # If flag = true -> there is another if statement but the block
                # is already eaten. To make sure we return to the appropriate
                # scope of the if block-statement, return statementlist according 
                # to the number of indent of the current if statement
                if self.flag == True and self.prevTempBlockChecker != 0:
                    self.prevTempBlockChecker -= 1
                    return statementList
                # If self.prevTempBlockChecker == 0, stop return statement,
                # we are already in the correct scope of the if statement
                else:
                    self.flag = False

                tempBlockChecker = 0
                # blockChecker is updated everytime a statement that requires
                # indentation is called
                # Loop through the indentation based on the correct indentation
                for i in range(self.blockChecker):
                    # If next token is not block anymore, break
                    if self.lookahead != None and \
                        self.lookahead.get('type') != 'block':
                        break
                    self.eat("block")
                    # Track how many loop there is currently
                    tempBlockChecker += 1
                
                # tempBlockChecker == 0 means that there is an if statement but the block
                # is already eaten, so we can just pass
                if tempBlockChecker == 0:
                    pass
                # If tempBlockChecker < the correct indentation, there are 2 possibilities
                # 1. Another if statement is called
                # 2. A syntax error
                elif tempBlockChecker < self.blockChecker:
                    
                    # If there is the current indent is < than expected indent
                    # Set prevTempBlocker to the difference between block checker
                    # and temp block checker - 1 because we return statementList 
                    # within the scope
                    self.prevTempBlockChecker = abs(self.blockChecker - tempBlockChecker - 1)
                    # Change current indentation to match
                    self.blockChecker = tempBlockChecker
                    # Set flag to True to loop again
                    self.flag = True
                    return statementList
                    
                # If there is still block, raise an indentation error
                if self.lookahead.get('type') == "block":
                    line, col = self.t.getIndex()
                    raise SyntaxError("Unmatched Indent Line: {} Col: {}".format(line, col))
                
                # Add statement to statement list      
                statementList.append(self.statement())
            # If the next statement is another if/def statement  and not in the same
            # scope, reset
            # if (self.lookahead != None and \
            #     self.lookahead.get('type') == "special-if") or \
            #     (self.lookahead != None and \
            #     self.lookahead.get('type') == "special-def"):
            self.blockChecker = 0   

        else:
            # If it is multiple statement
            # While we still have tokens, continue to loop (stop if cursor exceeds token)
            while (self.lookahead != None):
                # Append to list
                statementList.append(self.statement()) 
        return statementList
    
    def statement(self):
        # if self.lookahead.get('type') == "block":
        #     return self.blockStatement()
        if self.lookahead.get('type') == "special-if":
            return self.ifStatement()
        elif self.lookahead.get('type') == "special-def":
            return self.functionDeclaration()
        elif self.lookahead.get('type') == "return":
            return self.returnStatement()
        elif self.lookahead.get('type') == "identifier":
            return self.variableDeclaration()
        else:
            return self.expressionStatement()
    
    def blockStatement(self):
        body = []
        # self.eat('block') is called in statement list as there is a possibility
        # of multiple statements in a block statement
        if self.lookahead != None:
            # Combine the statement list into the body
            body += self.statementList("block")
            ast = {
                'type': 'BlockStatement',
                'body': body
            }
            return ast
        line, col = self.t.getIndex()
        raise SyntaxError("Invalid Syntax: BLock Statement Line: {} Col: {}".format(line, col))

    def ifStatement(self):
        expr = [] # What to test in the if statement
        body = [] # Content of if statement
        # Add 1 block token to each call of if statement
        self.blockChecker += 1
        # if-type Literal/ArithmeticExpr/BinaryExpr/LogicalExpr:
        # BlockStatement
        ifType = self.eat("special-if").get('value')
        # Syntax for if and elif
        if ifType == 'if' or ifType == 'elif':
            expr.append(self.expression())
            if self.lookahead != None:
                # If next token = ar operators, replace with Arithmetic Expr
                # If next token = com operators, replace with Binary Expr
                if self.lookahead.get('type') == 'ar-operators' or \
                    self.lookahead.get('type') == 'com-operators':
                    expr = self.expression(expr[-1])
                    # If next token is log operators, replace with Logical Expr  
                    if self.lookahead != None and \
                        self.lookahead.get('type') == 'log-operators':
                        expr = self.expression(expr)
                # If next token is log operators, replace with Logical Expr  
                elif self.lookahead != None and \
                    self.lookahead.get('type') == 'log-operators':
                    expr = self.expression(expr[-1])
                # If statement with literal
                elif 'Literal' in expr[-1].get('type'):
                    pass
                else:
                    line, col = self.t.getIndex()
                    raise SyntaxError("Invalid Syntax: If Statement Line: {} Col: {}".format(line, col))

        # Check for :
        if self.lookahead != None and \
            self.lookahead.get('type') == ':':
            # If statement syntax
            self.eat(':')
            self.eat('statement')
        else:
            line, col = self.t.getIndex()
            raise SyntaxError("Missing : Line: {} Col: {}".format(line, col))
        
        # Check for block statement
        if self.lookahead != None and \
            self.lookahead.get('type') == 'block':
            body.append(self.blockStatement())
        else:
            line, col = self.t.getIndex()
            raise SyntaxError("Block Statement Expected Line: {} Col: {}".format(line, col))
        
        ast = {
            'type': 'IfStatement',
            'if-type': ifType,
            'test': expr,
            'body': body
        }
        return ast


    def functionDeclaration(self):
        body = []
        funcId = ''
        params = []
        # def identifier(optionalVariable):
        # BlockStatement
        self.eat('special-def') # Eat def
        if self.lookahead != None:
            if self.lookahead.get('type') == 'identifier':
                # Check if identifier has been declared for function
                funcId = self.identifier(True, True)
            else:
                line, col = self.t.getIndex()
                raise SyntaxError("Identifier Expected Line: {} Col: {}".format(line, col))
            # Function Declaration syntax
            if self.lookahead != None and \
                self.lookahead.get('type') == '(':
                self.eat('(')
                # If there are parameters (e.g. identifier)
                if self.lookahead.get('type') == 'identifier':
                    # Loop until the end of params
                    while self.lookahead.get('type') == 'identifier':
                        # Check for duplicate params 
                        if self.lookahead.get('value') not in params:
                            # Append to params
                            params.append(self.lookahead.get('value'))
                            # Eat identifier
                            self.eat('identifier')
                            if self.lookahead.get('type') == ')':
                                break
                            # If there are more than 1 param
                            self.eat(',')
                        else:
                            line, col = self.t.getIndex()
                            raise SyntaxError("Duplicate Parameters Line: {} Col: {}".format(line, col))
            else:
                line, col = self.t.getIndex()
                raise SyntaxError("Missing ( Line: {} Col: {}".format(line, col))
            
            # Function Declaration syntax
            if self.lookahead != None and \
                self.lookahead.get('type') == ')':
                self.eat(')')
            else:
                line, col = self.t.getIndex()
                raise SyntaxError("Missing ) Line: {} Col: {}".format(line, col))

            if self.lookahead != None and \
                self.lookahead.get('type') == ':':
                self.eat(':')
                self.eat('statement')
            else:
                line, col = self.t.getIndex()
                raise SyntaxError("Missing : Line: {} Col: {}".format(line, col))
        else:
            line, col = self.t.getIndex()
            raise SyntaxError("Invalid Syntax: Function Declaration Line: {} Col: {}".format(line, col))

        # Add the correct indentation
        self.blockChecker += 1
        # Check for block statement
        if self.lookahead != None and \
            self.lookahead.get('type') == 'block':
            body.append(self.blockStatement())
            # for i in range(len(body)):
            #     if "ReturnStatement" in body[i].get('type'):
            #         print("hello")

        else:
            line, col = self.t.getIndex()
            raise SyntaxError("Block Statement Expected Line: {} Col: {}".format(line, col))
        
        # Add number of params 
        funcParams.append(len(params))
        ast = {
            'type': 'FunctionDeclaration',
            'funcId': funcId,
            'params': params,
            'body': body
        }
        return ast

    def returnStatement(self):
        self.eat("return")
        value = ''
        try:
            value = self.statement()
        except:
            line, col = self.t.getIndex()
            raise SyntaxError("Return Expression Expected Line: {} Col: {}".format(line, col))
        ast = {
            'type': 'ReturnStatement',
            'value': value,
        }
        return ast


    def variableDeclaration(self):
        tempVar = self.identifier(True)
        # If it is in a form of a list (happens when the result is 
        # CallExpression, get the first value)
        if type(tempVar) is list:
            tempVar = tempVar[0]
        tempVarValue = tempVar.get('value')

        # Call expression (inside expr statement)
        if tempVar.get('type') == 'ExpressionStatement':
            return tempVar

        if self.lookahead != None:
            # Check if it is variable declaration e.g. identifier = value
            if self.lookahead.get('type') == 'asg-operators' and self.lookahead.get('value') == '=':
                
                # Add the variable name to the list
                var.append(tempVarValue)
                self.eat("asg-operators")
                # Get the value
                try:
                    value = self.expressionStatement()

                    ast = {
                        'type': 'VariableDeclaration',
                        'variable' : var[-1],
                        'value': value
                    }
                    return ast
                # If there is no value, raise error
                except:
                    line, col = self.t.getIndex()
                    raise SyntaxError("Value Expected Line: {} Col: {}".format(line, col))

        # If not variable declaration, check if var exists
        if tempVarValue in var:
            # Call regular expression statement
            return self.expressionStatement(tempVar)
        # If it doesn't exist, raise error
        else:
            line, col = self.t.getIndex()
            raise SyntaxError("Variable doesn't exist Line: {} Col: {}".format(line, col))

    
    def expressionStatement(self, identifier=None, call=False):
        if identifier != None:
            # If it is call expression, directly return the ast
            if call == True:
                expr = [self.callExpression(identifier)]
                ast = {
                    'type': 'ExpressionStatement',
                    'expression': expr
                }
                return ast
            else:
                expr = [identifier]
        else:
            expr = [self.expression()]
        # Loop while hasn't reached end of file or end of statement 
        while self.lookahead != None and self.lookahead.get('type') != "statement":
            # If next token = ar operators, replace with Arithmetic Expr
            # If next token = com operators, replace with Binary Expr
            if self.lookahead.get('type') == 'ar-operators' or \
                self.lookahead.get('type') == 'com-operators':
                expr = [self.expression(expr[-1])]
                # If next token is log operators, replace with Logical Expr  
                if self.lookahead != None and \
                    self.lookahead.get('type') == 'log-operators':
                    expr = [self.expression(expr)]
                break

            # If next token is log operators, replace with Logical Expr  
            if self.lookahead != None and \
                self.lookahead.get('type') == 'log-operators':
                expr = [self.expression(expr[-1])]
                break
            # Append expression
            expr.append(self.expression(expr[-1]))
            # If reached end of file break from loop
            if self.lookahead == None:
                break
            
        ast = {
            'type': 'ExpressionStatement',
            'expression': expr
        }
        # If reached end of file return ast
        if self.lookahead == None:
            return ast
        # Else check for end of statement
        else:
            self.eat("statement")
        return ast
        
    def expression(self, expr=None):
        if self.lookahead.get('type') == 'ar-operators':
            return self.arithmeticExpression(expr)
        elif self.lookahead.get('type') == 'asg-operators':
            return self.operator('asg-operators')
        elif self.lookahead.get('type') == 'com-operators':
            return self.binaryExpression(expr)
        elif self.lookahead.get('type') == 'log-operators':
            return self.logicalExpression(expr)
        elif self.lookahead.get('type') == "special-func":
            return self.callExpression()
        elif self.lookahead.get('type') == 'identifier':
            return self.identifier()
        else:
            return self.literal()

    def arithmeticExpression(self, expr):
        tempExpr = []
        # Literal/Identifier <operator> Literal/Identifier
        if expr != None and 'Literal' in expr.get('type') or \
            expr != None and 'Identifier' in expr.get('type'):
            # Append token
            tempExpr.append(expr)
            # While haven't reached end of file and there are still
            # ar op, keep adding to tempExpr
            while self.lookahead != None and \
                self.lookahead.get('type') == 'ar-operators':
                tempExpr.append(self.operator('ar-operators'))
                # If haven't reached end of file
                if self.lookahead != None:
                    tempExpr.append(self.expression())
                    # Arithmetic expression syntax
                    if 'Literal' in tempExpr[-1].get('type') or \
                        'Identifier' in tempExpr[-1].get('type'):
                        pass
                else:
                    # If doesn't fulfill syntax
                    line, col = self.t.getIndex()
                    raise SyntaxError("Invalid Syntax: Arithmetic Expression Line: {} Col: {}".format(line, col))

            ast = {
                'type': 'ArithmeticExpression',
                'expression': tempExpr
            }
            return ast
        # If doesn't fulfill syntax
        line, col = self.t.getIndex()
        raise SyntaxError("Invalid Syntax: Arithmetic Expression Line: {} Col: {}".format(line, col))

    def binaryExpression(self, expr):
        tempExpr = []
        # Literal/Identifier <operator> Literal/Identifier
        if expr != None and 'Literal' in expr.get('type') or \
            expr != None and 'Identifier' in expr.get('type'):
            # Append token
            tempExpr.append(expr)
            # While haven't reached end of file and there are still
            # com op, keep adding to tempExpr
            while self.lookahead != None and \
                self.lookahead.get('type') == 'com-operators':
                tempExpr.append(self.operator('com-operators'))
                # If haven't reached end of file
                if self.lookahead != None:
                    tempExpr.append(self.expression())
                    # Binary expression syntax
                    if 'Literal' in tempExpr[-1].get('type') or \
                        'Identifier' in tempExpr[-1].get('type'):
                        pass
                else:
                    # If doesn't fulfill syntax
                    line, col = self.t.getIndex()
                    raise SyntaxError("Invalid Syntax: Binary Expression Line: {} Col: {}".format(line, col))

            ast = {
                'type': 'BinaryExpression',
                'expression': tempExpr
            }
            return ast
        # If doesn't fulfill syntax 
        line, col = self.t.getIndex()
        raise SyntaxError("Invalid Syntax: Binary Expression Line: {} Col: {}".format(line, col))
        
    def logicalExpression(self, expr):
        tempExpr = []
        # BinaryExpr/ArithmeticExpr <operator> BinaryExpr/ArithmeticExpr
        if expr != None and 'Binary' in expr.get('type') or \
            expr != None and 'Arithmetic' in expr.get('type') or \
                expr != None and 'Literal' in expr.get('type'):
            
            tempExpr.append(expr)
            while self.lookahead != None and \
                self.lookahead.get('type') == 'log-operators':
                tempExpr.append(self.eat('log-operators')) # Append logical op
                # While doesn't reach end of file
                if self.lookahead != None:
                    # Call next token to pass to binary expr
                    lastToken = self.expression()
                    # Check if the next token is com op
                    if self.lookahead.get('type') == 'com-operators':
                        # Check for binary expression and pass the last token
                        tempExpr.append(self.binaryExpression(lastToken))
                    # Check if the next token is ar op
                    elif self.lookahead.get('type') == 'ar-operators':
                        # Check for arithmetic expression and pass the last token
                        tempExpr.append(self.arithmeticExpression(lastToken))
                    else:
                        tempExpr.append(lastToken)
                else:
                    line, col = self.t.getIndex()
                    raise SyntaxError("Invalid Syntax: Logical Expression Line: {} Col: {}".format(line, col))
            ast = {
                'type': 'LogicalExpression',
                'expression': tempExpr
            }
            return ast
        # If doesn't fulfill syntax 
        line, col = self.t.getIndex()
        col -= len(self.lookahead.get('value'))
        raise SyntaxError("Invalid Syntax: Logical Expression Line: {} Col: {}".format(line, col))


    def operator(self, operator):
        token = self.eat(operator)
        ast = {
            'type': 'Operator',
            'value': token.get('value')
        }
        return ast
    
    def identifier(self, declaration = False, function = False):
        token = self.eat('identifier')
        value = token.get('value')
        # Skip checking for var declaration
        if declaration == False:
            if value not in var:
                line, col = self.t.getIndex()
                raise SyntaxError("Variable Not Declared Line: {} Col: {}".format(line, col))
        # Checking for function declaration
        if function == True:
            # If function id has not been used
            if function not in func:
                func.append(value)
            else:
                line, col = self.t.getIndex()
                raise SyntaxError("Duplicate Function Name Line: {} Col: {}".format(line, col))
        # Checking for call expression
        if self.lookahead != None and self.lookahead.get('type') == '(' \
            and function == False:
            return self.expressionStatement(value, call = True)

        ast = {
            'type': 'Identifier',
            'value': token.get('value')
        }
        return ast


    def callExpression(self, identifier = None):
        # Identifier(optionalParams)
        
        if self.lookahead.get('type') == 'special-func':
            input = ''
            funcId = self.eat('special-func')
            if self.lookahead != None and \
                self.lookahead.get('type') == '(':
                self.eat('(')
            else:
                line, col = self.t.getIndex()
                raise SyntaxError("Missing ( Line: {} Col: {}".format(line, col))
            if self.lookahead.get('type') == 'identifier':
                input = self.identifier(True)
            else:
                try:
                    input = self.expression()
                except:
                    pass
            if self.lookahead != None and \
                self.lookahead.get('type') == ')':
                self.eat(')')
            else:
                line, col = self.t.getIndex()
                raise SyntaxError("Missing ) Line: {} Col: {}".format(line, col))
            ast = { 
                'type': 'CallExpression',
                'funcId': funcId,
                'input': input
            }
            return ast
        # If it is other function calling
        elif identifier != None and identifier in func:
            params = [] # Check for params
            checker = 0 # Counter for current param      
            # Check how many parameters the function is expecting
            index = funcParams[func.index(identifier)]

            self.eat('(')
            # If expecting params
            if index != 0:
                # Loop as many times as params expected
                for i in range(index):
                    try:
                        # Call self.expression()
                        params.append(self.expression())
                    except:
                        # If there is no params, break to return error
                        break
                    # Add checker as we have already get 1 param
                    checker += 1
                    # If it is not , break
                    if self.lookahead.get('type') != ',':
                        break
                    self.eat(',')

                # If there is still more parameters  
                if self.lookahead.get('type') != ')':
                    line, col = self.t.getIndex()
                    raise SyntaxError("Too Many Parameters Line: {} Col: {}".format(line, col))
                # If there is too less parameters
                if checker < index:
                    line, col = self.t.getIndex()
                    raise SyntaxError("Missing Parameters Line: {} Col: {}".format(line, col))
            if self.lookahead != None and self.lookahead.get('type') == ')':
                self.eat(')')
            else:
                line, col = self.t.getIndex()
                raise SyntaxError("Missing ) Line: {} Col: {}".format(line, col))
            ast = {
                'type': 'CallExpression',
                'value': identifier,
                'params': params,
            }
            return ast
        else:
            line, col = self.t.getIndex()
            raise SyntaxError("Function Doesn't Exist Line: {} Col: {}".format(line, col))
    
    def literal(self):
        # Get token type
        tokenType = self.lookahead.get('type')
        if tokenType == 'NUMBER':
            return self.numericalLiteral()
        elif tokenType == 'STRING':
            return self.stringLiteral()
        elif tokenType == 'BOOLEAN':
            return self.booleanLiteral()
        elif tokenType == 'NONE':
            return self.noneLiteral()
        # If none of the token type matches
        else:
            print(tokenType)
            line, col = self.t.getIndex()
            raise ValueError("Unsupported Literal Type Line: {} Col: {}".format(line, col))

    def numericalLiteral(self):
        token = self.eat('NUMBER')   
        ast = {
            'type': 'NumericalLiteral',
            'value': token.get('value')
        }
        return ast
    
    def stringLiteral(self):
        token = self.eat('STRING')
        ast = {
            'type': 'StringLiteral',
            'value': token.get('value')[1:-1] # To not include the ""
        }
        return ast

    def booleanLiteral(self):
        token = self.eat('BOOLEAN')
        ast = {
            'type': 'BooleanLiteral',
            'value': token.get('value')
        }
        return ast

    def noneLiteral(self):
        token = self.eat('NONE')
        ast = {
            'type': 'NoneLiteral',
            'value': token.get('value')
        }
        return ast

    # Function to consume token type and check with the input
    # Then get next token
    def eat(self, tokenType):
        token = self.lookahead
        # If reached end of file
        if token == None:
            line, col = self.t.getIndex()
            raise ValueError("Reached End of File Line: {} Col: {}".format(line, col)) 
        # Different token type from input
        if token.get('type') != tokenType:
            print(tokenType, token)
            line, col = self.t.getIndex()
            raise ValueError("Unmatched Token Value Line: {} Col: {}".format(line, col))
        # Get the next text
        self.lookahead = self.t.getNextToken('eat')
        return token
