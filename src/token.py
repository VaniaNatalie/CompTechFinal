import re

# Tokenizer regex rules
tokenRegex = [
    # -- BLock statement --
    ["indent", "^[^\S\n]{4}"], # Indent marks block statement
    # -- Delimiter -- 
    ["statement", "^\n"], # As python doesn't really have a delimeter to mark the end of a statement, we assigned \n as the delimeiter
    # -- Whitespace --
    [None, "^[^\S\n]+"], # None is for skippable contents
    # -- Comments --
    # Single-line comments
    [None, "^#.*"],
    # Multi-line comments
    [None, "^'''[\s\S]*'''"],
    [None, '^"""[\s\S]*"""'],
    # -- Numbers --
    ["NUMBER", "^\d+"],
    # -- String -- 
    ["STRING", '^"[^"]*"'],
    ["STRING", "^'[^']*'"]
]

# Tokenizer
class Token:
    def __init__ (self, s):
        self.s = s
        self.cursor = 0
        self.tokenTypePrev = ''
    
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

    def getNextToken(self, info):
        # if cursor exceeds the word or has reached end of file
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
            # Check for block statement that starts with indent nd needs to start after statement 
            if tokenType == "indent" and self.tokenTypePrev == "statement":
                print("block")
                ast = {'type': "block", 'value': tokenValue}
                return ast
            # Skip token, used for whitespaces, comments
            elif tokenType == None:
                self.getNextToken('whitespace')
            # If token valid
            else:
                # Store current token type 
                self.tokenTypePrev = tokenType
                ast = {'type': tokenType, 'value': tokenValue}
                return ast
        raise ValueError("Unexpected Token {}".format(self.s[0]))