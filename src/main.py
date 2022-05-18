from parse import Parse

with open("test.txt", "r") as f:
    data = f.read()

p = Parse(data)
print(p.parsee())

    #hello
    