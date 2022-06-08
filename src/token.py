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
    ["special", "^(if|elif|else)"],
    [":", "^:"],
    ["(", "^\("],
    [")", "^\)"],

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
        self.s = s
        self.cursor = 0
        self.tokenTypePrev = ''
        self.blockChecker = 0
    
    # Check if tokenType matches with any tokenType stated already in rules (tokenRegex)
    def regexMatch(self, pattern, string):
        # Match pattern with string
        match = re.match(pattern, string)
        if match:
            # Move cursor position to end of matched string
            self.cursor += len(match.group())
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
            
            # Checking for block
            if self.checkBlockStatement(tokenType, tokenValue):
                self.tokenTypePrev = tokenType
                # Return block token
                ast = {'type': "block", 'value': tokenValue}
                return ast

            # For skippable contents
            elif tokenType == None or tokenType == "whitespace" or \
                tokenType == "indent":
                nextToken = self.getNextToken('whitespace')
                # If next token after whitespace is statement (\n)
                if nextToken != None and nextToken.get('type') == 'statement':
                    # Change to None so at the next iter it can be skipped
                    nextToken['type'] = None
                    # Get next token to skip
                    return self.getNextToken('whitespace')
            
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