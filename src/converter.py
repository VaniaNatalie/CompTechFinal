import enum

class Syntax(enum.Enum):
    Program = "Program"
    IfStatement = "IfStatement"

Statements = [
    Syntax.Program,
    Syntax.IfStatement,
]

# Converter
class Convert:
    def __init__(self, ast):
        self.ast = ast
        self.indentation = 0
        self.indent = 5

    # C++ Header
    def create_header(self):
        return '#include <iostream>\nusing namespace std;\n'

    # C++ main function
    def create_main(self, statement):
        res = ['\n\nint main(void) {\n']

        for i in statement.get('body'):
            # Declare variable
            if i['type'] == 'VariableDeclaration':
                res.append(self.variabledeclaration(i))
            # Print and Input call
            if i['type'] == 'ExpressionStatement':
                for j in i['expression']:
                    if j['type'] == 'CallExpression':
                        res.append("{}{}\n".format(self.indent * " ", self.callexpression(j)))
        
        res.append(f'{self.indent * " "}return 0;\n')
        res.append('}')
        return res

    # Function to help translate if-type in C++
    def translate_if_type(self, if_type):
        if if_type == "elif":
            return "else if"
        else:
            return if_type

    # Check statement type from ast
    def check_statement(self, statement):
        return Syntax(statement["type"]) in Statements

    # Function to help translate identifier in C++
    def create_identifier(self, node):
        value = str(node['value'])
        if value == "print":
            value = value.replace('print', 'cout <<')
        if value == 'input':
            value = value.replace('input', 'cin >>')   
        return value

    # Function to help format the input
    def create_input(self, node):
        value_type = str(node['type'])
        value = ''
        if value_type == 'ExpressionStatement':
            for i in node['expression']:
                variable_type = i['type']
                if variable_type == 'CallExpression':
                    value = i['value']
                continue

            value = '{}()'.format(value)
        if value_type == 'BooleanLiteral':
            value = str(node['value']).lower()
        if value_type == "StringLiteral":
            value = '"{}"'.format(str(node['value']))
        if value_type == 'NumericalLiteral':
            value = str(node['value'])
        return value
    
    # Function to create function params
    def create_function_param(self, node):
        params = []
        for param in node['params']:
            # print(param)
            params.append(param)
        return '(' + ", ".join(params) + ')'

    # Function to be called to call function
    def create_statement(self, statement):
        node_type = statement["type"]
        # For expression
        if node_type.lower().endswith('expression'):
            return self.create_expression(statement)
        attr = getattr(self, node_type.lower())
        return attr(statement)

    def create_expression(self, expr):
        node_type = expr['type']
        attr = getattr(self, node_type.lower())
        return attr(expr)

    # Program function (starting function)
    def program(self, statement):
        res = []
        main_res = []
        res.append(self.create_header())
        for i in statement.get('body'):
            value_type = i['type']
            if value_type == 'ExpressionStatement':
                continue

            if value_type != 'VariableDeclaration': 
                res += self.create_statement(i)
       
        for j in self.create_main(statement):
            main_res += j
        final_res = res + main_res
        return "".join(final_res)

    # Function declaration (header)
    def functiondeclaration(self, statement): 
        return f"\nvoid {self.create_identifier(statement['funcId'])}{self.create_function_body(statement)}" 
    
    # Function body
    def create_function_body(self, node):
        body_res = []
        # print(node['body'])
        for i in node.get('body'):
            body_res += self.create_statement(i)
        body = "".join(body_res)
        result = [self.create_function_param(node), body]
        return "".join(result)

    # If body
    def create_if_body(self, node):
        body_res = []
        # print(node)
        for i in node.get('body'):
            body_res += self.create_statement(i)
    
        return "".join(body_res)

    # If statement
    def ifstatement(self, statement):
        result = ''
        if statement['test']:
            result = f"{self.translate_if_type(statement['if-type'])} ({self.create_expression(statement['test'])})"
            result += self.create_if_body(statement)
        # for 'else'
        else:
            result = f"{self.translate_if_type(statement['if-type'])}"
            result += self.create_if_body(statement)
        return result

    # Block statement
    def blockstatement(self, statement):
        res = [" {\n"]
        self.indentation += self.indent
        for body_statement in statement['body']:
            res.append('{}{}\n'.format((self.indentation * " "), self.create_statement(body_statement)))
        self.indentation -= self.indent
        res.append("%s}\n" % (self.indentation * " "))
        res = "".join(res)
        return res

    # Binary expression 
    def binaryexpression(self, expr):
        res = []
        for i in expr.get('expression'):
            res += self.create_statement(i)
        return "".join(res)

    # Expression statement
    def expressionstatement(self, statement):
        res = []
        for i in statement.get('expression'):
            res += self.create_expression(i)
        return "".join(res)

    # Return statement
    def returnstatement(self, statement):
        result = f'{self.indent * ""}'
        if statement['value']:
            result += "return {};".format(self.create_expression(statement['value']))
        else:
            result += 'return;'
        return result

    # Arithmetic expression
    def arithmeticexpression(self, expr):
        res = []
        for i in expr.get('expression'):
        #     print(i)
            res.append(self.create_statement(i))
        return "".join(res)

    # Call expression
    def callexpression(self, expr):
        res = f'{self.indent * ""}'
        # print(expr['input']['type'])

        # if print() or input() is called
        if 'funcId' in expr:
            # if it has parameter 
            if 'expression' in expr['input']:
                for i in expr['input']['expression']:
                    # if only one parameter
                    if len(i['params']) == 1:
                        value_type = i['params'][0]['type']
                        value = i['params'][0]['value']
                        if value_type == 'StringLiteral':
                            value = '"{}"'.format(value)
                        if value_type == 'BooleanLiteral':
                            value = value.lower()
                        res += '{} {}({});'.format(self.create_identifier(expr['funcId']), i['value'], value)
                    # more than one parameter 
                    else:
                        # to store the parameter
                        store_value = []
                        for j in i['params']:
                            value_type = j['type']
                            value = j['value']
                            if value_type == 'StringLiteral':
                                value = '"{}"'.format(value)
                            if value_type == 'BooleanLiteral':
                                value = value.lower()
                            store_value.append(value)
                        # join the array's value and make a string sep with commas
                        joined_value = ', '.join(store_value)
                        res += '{} {}({});'.format(self.create_identifier(expr['funcId']), i['value'], joined_value)
            # no parameter
            else:
                res += '{} {};'.format(self.create_identifier(expr['funcId']), self.create_input(expr['input']))
        # no print() or input() called
        else:
            # no params
            if len(expr['params']) == 0:
                res += '{}();'.format(expr['value'])
            # has params
            else:
                # if there's only one param
                if len(expr['params']) == 1:
                    value_type = expr['params'][0]['type']
                    value = expr['params'][0]['value']
                    if value_type == 'StringLiteral':
                        value = '"{}"'.format(value)
                    if value_type == 'BooleanLiteral':
                        value = value.lower()
                    res += '{}({});'.format(expr['value'], value)
                # has more than one param
                else:
                    # to store the parameter
                    store_value = []
                    for i in expr['params']:
                        value_type = i['type']
                        value = i['value']
                        if value_type == 'StringLiteral':
                            value = '"{}"'.format(value)
                        if value_type == 'BooleanLiteral':
                            value = value.lower()
                        store_value.append(value)
                    # join the array's value and make a string sep with commas
                    joined_value = ', '.join(store_value)
                    res += '{}({});'.format(expr['value'], joined_value)               
        return res

    # Variable declaration
    def variabledeclaration(self, statement):
        var_type = ''
        variable_name = statement['variable']
        variable_value = self.create_expression(statement['value'])
        for i in statement['value']['expression']:
            variable_type = i['type']
        # Translate value type for variable declaration
        if variable_type == 'NumericalLiteral':
            var_type += 'int'
        if variable_type == 'StringLiteral':
            var_type += 'string'
        if variable_type == 'BooleanLiteral':
            var_type += 'bool'
        res = f'{self.indent * " "}'
        res += '{} {} = {};\n'.format(var_type, variable_name, variable_value)
        return res

    # Numerical literal
    def numericalliteral(self, node):
        res = str(node["value"])
        return res

    # Operator
    def operator(self, node):
        res = str(node["value"])
        return res

    # String literal
    def stringliteral(self, node):
        return '"{}"'.format(str(node['value']))

    # Boolean literal
    def booleanliteral(self, node):
        return str(node['value']).lower()

    # Convert function to call the program
    def convert(self):
        if self.check_statement(self.ast):
            return self.create_statement(self.ast)
        else:
            print("Invalid", self.ast["type"])
        pass