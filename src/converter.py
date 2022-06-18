class Convert:
    def __init__(self, s):
        self.s = s
        self.output = '#include <iostream>\nusing namespace std;\n'

    def convert(self):
        return self.output