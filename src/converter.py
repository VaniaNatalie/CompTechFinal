import enum


class Syntax(enum.Enum):
    Program = "Program"
    IfStatement = "IfStatement"

Statements = [
    Syntax.Program,
    Syntax.IfStatement,
]

class Convert:
    def __init__(self, ast):
        self.ast = ast
        self.indentation = 0
        self.indent = 5

    def create_header(self):
        return '#include <iostream>\nusing namespace std;\n'

    def create_main(self, statement):
        res = ['\n\nint main(void) {\n']

        for i in statement.get('body'):
            if i['type'] == "FunctionDeclaration":
                res.append("%s%s();\n" % (self.indent * " ",self.create_identifier(i['funcId'])))
            if i['type'] == 'VariableDeclaration':
                res.append(self.variabledeclaration(i))
            if i['type'] == 'ExpressionStatement':
                for j in i['expression']:
                    if j['type'] == 'CallExpression':
                        res.append("{}{}\n".format(self.indent * " ", self.callexpression(j)))
        
        res.append(f'{self.indent * " "}return 0;\n')
        res.append('}')
        return res

    def translate_if_type(self, if_type):
        if if_type == "elif":
            return "else if"
        else:
            return if_type

    def check_statement(self, statement):
        return Syntax(statement["type"]) in Statements

    def create_identifier(self, node):
        value = str(node['value'])
        if value == "print":
            value = value.replace('print', 'cout <<')
        if value == 'input':
            value = value.replace('input', 'cin >>')   
        return value

    def create_input(self, node):
        value = str(node['value'])
        value_type = str(node['type'])
        if value_type == 'BooleanLiteral':
            value = value.lower()
        if value_type == "StringLiteral":
            value = '"{}"'.format(value)
        if value_type == 'CallExpression':
            value = '{}()'.format(value)
        return value
    
    def create_function_param(self, node):
        params = []
        for param in node['params']:
            # print(param)
            params.append(param)
        return '(' + ", ".join(params) + ')'

    def create_statement(self, statement):
        node_type = statement["type"]
   
        if node_type.lower().endswith('expression'):
            return self.create_expression(statement)
        attr = getattr(self, node_type.lower())
        return attr(statement)

    def create_expression(self, expr):
        node_type = expr['type']
        attr = getattr(self, node_type.lower())
     
        return attr(expr)

    def program(self, statement):
        res = []
        main_res = []
        res.append(self.create_header())
        call_expression = ''
        for i in statement.get('body'):
            if i['type'] == 'ExpressionStatement':
                for k in i['expression']:
                    if k['type'] == 'CallExpression':
                       call_expression = k['type']
                continue
            if i['type'] != 'VariableDeclaration' or call_expression != 'CallExpression':
                res += self.create_statement(i)
            else:
                pass
        for j in self.create_main(statement):
            main_res += j
        final_res = res + main_res
        return "".join(final_res)

    def functiondeclaration(self, statement): 
    
        return f"\nvoid {self.create_identifier(statement['funcId'])}{self.create_function_body(statement)}" 
    
    def create_function_body(self, node):
        body_res = []
        # print(node['body'])
        for i in node.get('body'):
            body_res += self.create_statement(i)
        body = "".join(body_res)
      
        result = [self.create_function_param(node), body]
        return "".join(result)

    def create_if_body(self, node):
        body_res = []
        # print(node)
        for i in node.get('body'):
            body_res += self.create_statement(i)
    
        return "".join(body_res)

    def ifstatement(self, statement):
        result = ''
        if statement['test']:
            result = f"{self.translate_if_type(statement['if-type'])} ({self.create_expression(statement['test'])})"
            result += self.create_if_body(statement)
        else:
            result = f"{self.translate_if_type(statement['if-type'])}"
            result += self.create_if_body(statement)
        return result

    def blockstatement(self, statement):
        res = [" {\n"]
        self.indentation += self.indent
        for body_statement in statement['body']:
            res.append('{}{}\n'.format((self.indentation * " "), self.create_statement(body_statement)))
        self.indentation -= self.indent
        res.append("%s}\n" % (self.indentation * " "))
        res = "".join(res)
        return res
        
    def binaryexpression(self, expr):
        res = []
        for i in expr.get('expression'):
            res += self.create_statement(i)
        return "".join(res)

    def expressionstatement(self, statement):
        res = []
        for i in statement.get('expression'):
            res += self.create_expression(i)
        return "".join(res)

    def returnstatement(self, statement):
        result = f'{self.indent * ""}'
        if statement['value']:
            result += "return {};".format(self.create_expression(statement['value']))
        else:
            result += 'return;'
        return result

    def arithmeticexpression(self, expr):
        res = []
        for i in expr.get('expression'):
        #     print(i)
            res.append(self.create_statement(i))
        return "".join(res)

    def callexpression(self, expr):
        res = f'{self.indent * ""}'
        # print(expr['input']['type'])

        res += '{} {};'.format(self.create_identifier(expr['funcId']), self.create_input(expr['input']))
        return res

    def variabledeclaration(self, statement):
        var_type = ''
        variable_name = statement['variable']
        variable_value = self.create_expression(statement['value'])
        for i in statement['value']['expression']:
            variable_type = i['type']
        if variable_type == 'NumericalLiteral':
            var_type += 'int'
        if variable_type == 'StringLiteral':
            var_type += 'string'
        if variable_type == 'BooleanLiteral':
            var_type += 'bool'
        res = f'{self.indent * " "}'
        res += '{} {} = {};\n'.format(var_type, variable_name, variable_value)
        return res

    def numericalliteral(self, node):
        res = str(node["value"])
        return res

    def operator(self, node):
        res = str(node["value"])
        return res

    def stringliteral(self, node):
        return '"{}"'.format(str(node['value']))

    def booleanliteral(self, node):
        return str(node['value']).lower()

    def convert(self):
        if self.check_statement(self.ast):
            return self.create_statement(self.ast)
        else:
            print("Unknown", self.ast["type"])
        pass