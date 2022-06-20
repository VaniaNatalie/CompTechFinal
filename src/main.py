
from parse import Parse
from converter import Convert
import json

with open("test.txt", "r") as f:
    data = f.read()

# Parsing data
p = Parse(data)
parsedData = p.parsee()
print(parsedData)
# parsedJson = json.dumps(parsedData)

# Converting data
# c = Convert(parsedData)
# print(c.convert())

# for key, val in parsedData:
#     print(val)
    #hello
    