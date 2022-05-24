from token import Token

# Parser
class Parse:   
    def __init__ (self, s):
        # string input
        self.s = s 
        # token object
        self.t = Token(self.s)

    
    # Main entry point
    def parsee(self):     
        # previous number indentation
        self.blockChecker = 0
        # block checker flag 
        self.tempBlockChecker = False
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
        statementList = [self.statement()]

        # If checking for block statement
        if blockStatementStopper != None:
            # While not reached end of file and there is indentation or tempBlockChecker is True
            while ((self.lookahead != None and self.lookahead.get('type') == blockStatementStopper) or self.tempBlockChecker == True):
                if self.tempBlockChecker == False:
                    # Try looping the indentation based on the previous number of indentation
                    try:
                        for i in range(self.blockChecker):
                            self.eat("block")
                    
                    # If number of current indentation < previous number of indentation
                    except:
                        # Decrease the previos number of indentation 
                        self.blockChecker -= 1
                        # Set tempBlockChecker to True becuase we are going to need 
                        # to add the current statement to previous block statement
                        self.tempBlockChecker = True
                        # Return statement list (which only contains one statement) 
                        # and break out of loop
                        return statementList
                    
                    # If current indentation = previous number of indentation           
                    statementList.append(self.statement())

                # If tempBlockChecker = True
                else:
                    # Append statement to statementList
                    statementList.append(self.statement())
                    # Set flag to False
                    self.tempBlockChecker = False

            ''' 
            NOTE!!!
            Why do we need to have tempBlockChecker/flag?
            It is useful in scenarios like:
                1
                        2
                3
            Without tempBlockChecker, after we break out of loop for statement 2,
            the block in statement 3 can no longer be detected because it has 
            been eaten (self.eat("block")) when checking for number of indentation
            (for i in range(self.blockChecker)).
            We need statement 1 to still detect statement 3 as part of its
            block statement, however, without the block at the beginning of 
            statement 3, it can no longer loop (because we only check 
            self.lookahead.get('type') == blockStatementStopper). Hence, we added
            a flag to let the program loop and add statement 3 to block statement 1.
            '''   
                
        else:
            # If it is multiple statement
            # While we still have tokens, continue to loop (stop if cursor exceeds token)
            while (self.lookahead != None):
                # Append to list
                statementList.append(self.statement()) 
        # tempBlockChecker = False   
        return statementList
    
    def statement(self):
        if self.lookahead.get('type') == "block":
            return self.blockStatement()
        else:
            return self.expressionStatement()
    
    def blockStatement(self):
        body = []
        self.blockChecker += 1
        # While there are still statements in the block statement (or there is indentation)
        # Check the indentation
        self.eat("block")
        # Combine the statement list into the body
        body += self.statementList("block")
        ast = {
            'type': 'BlockStatement',
            'body': body
        }
        return ast
    
    def expressionStatement(self):
        expr = [self.expression()]
        # As \n isn't exactly the delimiter for python, the last statement in the source code that doesn't end with \n should be valid
        # To ensure that, we will run .eat() after checking that the token doesn't return None (or the cursor exceeds the input)
        if self.lookahead != None:
            try:
                self.eat("statement")
            # In cases where there are more than one 
            except:
                expr.append(self.expression())

        ast = {
            'type': 'ExpressionStatement',
            'expression': expr
        }
        return ast
        
    def expression(self):
        if self.lookahead.get('type') == 'operators':
            return self.operator()
        else:
            return self.literal()

    def operator(self):
        token = self.eat('operators')
        ast = {
            'type': 'Operator',
            'value': token.get('value')
        }
        return ast
    
    def literal(self):
        # Get token type
        tokenType = self.lookahead.get('type')
        if tokenType == 'NUMBER':
            return self.numericalLiteral()
        elif tokenType == 'STRING':
            return self.stringLiteral()
        # If none of the token type matches
        else:
            raise ValueError("Unsupported Literal Type")

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

    def eat(self, tokenType):
        token = self.lookahead
        if token == None:
            raise ValueError("Reached End of File") 
            
        # Different token type from input
        if token.get('type') != tokenType:
            raise ValueError("Unmatched Token Value")
        self.lookahead = self.t.getNextToken('eat')
        return token
