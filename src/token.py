import re

# Tokenizer regex rules
tokenRegex = [
    # -- BLock statement --
    ["indent", "^[^\S\n]{4}"], # Indent marks block statement
    # -- Delimiter -- 
    ["statement", "^\n"], # As python doesn't really have a delimeter to mark the end of a statement, we assigned \n as the delimeiter
    # -- Whitespace --
    ["whitespace", "^[^\S\n]+"], # None is for skippable contents 

    # -- Special Keywords and Symbols--
    ["special-if", "^(if|elif|else)"],
    ["special-func", "^(print|input)"],
    ["special-def", "^def"],
    ["return", "^return"],
    [":", "^:"],
    ["(", "^\("],
    [")", "^\)"],
    [",", "^,"],

    # -- Operators --
    # Comparison Operators
    ["com-operators", "^(<=|>=|<|>|==|!=)"],
    # Assignment Operators
    ["asg-operators", "^(=|\+=|-=|\/=|%=)"],
    # Arithmetic Operators
    ["ar-operators", "^(\+|\-|\*|\/)"],
    # Logical Operators
    ["log-operators", "^(and|or)"],


    # -- Comments --
    # Single-line comments
    [None, "^#.*"],
    # Multi-line comments
    [None, "^'''[\s\S]*'''"],
    [None, '^"""[\s\S]*"""'],

    # -- LITERALS -- 
    # -- Numbers --
    ["NUMBER", "^\d+"],
    # -- String -- 
    ["STRING", '^"[^"]*"'],
    ["STRING", "^'[^']*'"],
    # -- Boolean --
    ["BOOLEAN", "^(True|False)"],
    # -- None --
    ["NONE", "^None"],

    # -- Identifier --
    ["identifier","^[^_!.@=%$'\"][A-Z_*a-z]+\d*"],
]

# Tokenizer
class Token:
    def __init__ (self, s):
        self.s = s # Input string
        self.cursor = 0 # Current index
        self.tokenTypePrev = '' # Previous token type
        self.blockChecker = 0 # Block checking
        self.prevLine = 0 # Previous line index
        self.line = 1 # Current line index, start count from 1
        self.prevCol = 0 # Previous column index
        self.col = 0 # Current col index, start count from 1
    
    # Check if tokenType matches with any tokenType stated already in rules (tokenRegex)
    def regexMatch(self, pattern, string):
        # Match pattern with string
        match = re.match(pattern, string)
        if match:
            # Move cursor position to end of matched string
            self.cursor += len(match.group())
            # Add col based on cursor
            self.col += self.cursor
            # Return the value
            return match.group()
        return None

    # Check for block statements
    def checkBlockStatement(self, type, value):
        # Check for block statement that starts with indent and needs to start after statement 
        # or check for block statement that starts with indent and indent
        if type == "indent" and (self.tokenTypePrev == "statement" \
            or self.tokenTypePrev == "indent"):
            return True
        # If there is a whitespace after indent that != indent
        elif self.tokenTypePrev == "indent" and type == "whitespace":
            raise SyntaxError("Indentation Error")

    def getNextToken(self, info):
        # If cursor exceeds the word or has reached end of file
        if self.cursor >= len(self.s):
            return None
        self.s = self.s[self.cursor:]

        # Regex rules
        for [tokenType, regexp] in tokenRegex:
            self.cursor = 0
            # Get the value
            tokenValue = self.regexMatch(regexp, self.s)
            
            # If doesn't match, continue
            if tokenValue == None:
                continue
            
            # Add line and reset col every statement
            if tokenType == "statement":
                # Store previous line and col
                self.prevLine = self.line
                self.prevCol = self.col - 1 # -1 because cursor is always ahead by 1

                self.line += 1
                self.col = 0
            
            # Checking for block
            if self.checkBlockStatement(tokenType, tokenValue):
                self.tokenTypePrev = tokenType
                # Return block token
                ast = {'type': "block", 'value': tokenValue}
                return ast

            # For skippable contents
            elif tokenType == None or tokenType == "whitespace" or \
                tokenType == "indent":
                return self.getNextToken('whitespace')
                # # If next token after whitespace is statement (\n)
                # if nextToken != None and nextToken.get('type') == 'statement':
                #     # Change to None so at the next iter it can be skipped
                #     nextToken['type'] = None
                #     # Get next token to skip
                #     return self.getNextToken('whitespace')
            
            # For empty lines
            elif self.tokenTypePrev == "statement" and tokenType == "statement":
                tokenType = None
                # Get next statement to skip
                return self.getNextToken('whitespace')
                
            # If token valid
            else:
                # Store current token type 
                self.tokenTypePrev = tokenType
                ast = {'type': tokenType, 'value': tokenValue}
                return ast
        raise ValueError("Unexpected Token {}".format(self.s[0]))

    # Get line and col for error handling
    def getIndex(self):
        # If prev token type is statement (means error occurs at the 
        # end of statement), call prev line and prev col (as line and col
        # is added and reset respectively everytime a statement ends, calling
        # line and col will not display the index where the orrur occurs)
        if self.tokenTypePrev == 'statement':
            return self.prevLine, self.prevCol
        # Else prev token type not statement, return current index
        else:
            return self.line, self.col