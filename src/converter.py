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
        return '#include <iostream>\nusing namespace std;\n\n'

    def create_main(self, statement):
        res = ['\n\nint main(void) {\n']

        for i in statement.get('body'):
            if i['type'] == "FunctionDeclaration":
                res.append("%s%s();\n" % (self.indent * " ",self.create_identifier(i['funcId'])))
        
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
        return str(node["value"])
    
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
        # print(attr())
        # print(attr)
        return attr(statement)

    def create_expression(self, expr):
        node_type = expr["type"]
        print(node_type)
        attr = getattr(self, node_type.lower())
        return attr(expr)

    def program(self, statement):
        res = []
        main_res = []
        res.append(self.create_header())
        for i in statement.get('body'):
            # print(i)
            res += self.create_statement(i)
        for j in self.create_main(statement):
            main_res += j
        final_res = res + main_res
        return "".join(final_res)

    def functiondeclaration(self, statement):
        return f"void {self.create_identifier(statement['funcId'])}{self.create_function_body(statement)}" 
    
    def create_function_body(self, node):
        body_res = []
        print(node['body'])
        for i in node.get('body'):
            body_res += self.create_statement(i)
        body = "".join(body_res)
      
        result = [self.create_function_param(node), body]
        return "".join(result)

    def create_if_body(self, node):
        body_res = []
        print(node)
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
        return self.create_statement(statement['expression'])

    def returnstatement(self, statement):
        result = f'{self.indent * " "}'
        if statement['value']:
            result += "return {};".format(self.create_expression(statement['value']))
        else:
            result += 'return;'
        return result

    def arithmeticexpression(self, expr):
        res = []
        for i in expr.get('expression'):
            res += self.create_statement(i)
        return "".join(res)

    def numericalliteral(self, node):
        return str(node["value"])

    def operator(self, node):
        return str(node['value'])

    def stringliteral(self, node):
        return '"{}"'.format(str(node['value']))

    def convert(self):
        if self.check_statement(self.ast):
            return self.create_statement(self.ast)
        else:
            print("Unknown", self.ast["type"])
        pass