from token import Token

# Parser
class Parse:   
    def __init__ (self, s):
        self.s = s
        self.t = Token(self.s)
    
    # Main entry point
    def parsee(self):     
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
            # While not reached end of file and there is indentation
            while (self.lookahead != None and self.lookahead.get('type') == blockStatementStopper):
                # Check the indentation
                self.eat("block")
                # Append to list
                statementList.append(self.statement())   
        else:
            # If it is multiple statement
            # While we still have tokens, continue to loop (stop if cursor exceeds token)
            while (self.lookahead != None):
                # Append to list
                statementList.append(self.statement())    
        return statementList
    
    def statement(self):
        if self.lookahead.get('type') == "block":
            return self.blockStatement()
        else:
            return self.expressionStatement()
    
    def blockStatement(self):
        # Check for beginning of block statement (indentation)
        self.eat("block")
        # Add the statement into the body
        body = [self.statement()]
        # While there are still statements in the block statement (or there is indentation)
        if self.lookahead.get('type') == "block":
            # Check the indentation
            self.eat("block")
            # Combine the statement list into the body
            body += self.statementList("block")
        ast = {
            'type': 'blockStatement',
            'body': body
        }
        return ast
    
    def expressionStatement(self):
        expr = self.expression()
        
        # As \n isn't exactly the delimiter for python, the last statement in the source code that doesn't end with \n should be valid
        # To ensure that, we will run .eat() after checking that the token doesn't return None (or the cursor exceeds the input)
        if self.lookahead != None:
            self.eat("statement")
        ast = {
            'type': 'ExpressionStatement',
            'expression': expr
        }
        return ast
        
    def expression(self):
        return self.literal()
    
    def literal(self):
        # Get token type
        tokenType = self.lookahead.get('type')
        if tokenType == 'NUMBER':
            return self.numericalLiteral()
        elif tokenType == 'STRING':
            return self.stringLiteral()
        # If none of the token type matches
        else:
            print(tokenType)
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
            raise ValueError("error") 
            
        # Different token type from input
        if token.get('type') != tokenType:
            raise ValueError("Unmatched Token Value")
        val = 'token' + tokenType
        self.lookahead = self.t.getNextToken(val)
        return token
