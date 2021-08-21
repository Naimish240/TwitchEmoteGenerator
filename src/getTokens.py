import pandas as pd
import re

count = 25

df = pd.read_csv('file1.csv')
emotes = df.ename

tokens = {}

for name in emotes:
    foo = [i.lower() for i in re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', name)).split()]
    for i in foo:
        if i not in tokens.keys():
            tokens[i] = 1
        else:
            tokens[i] += 1

# print("Number of Unique tokens: ", len(tokens))

token_tuple = [(v, k) for v, k in tokens.items()]
token_tuple.sort(key=lambda x: x[1], reverse=True)
print(token_tuple[:count])

print(sum([k for (v, k) in token_tuple[:count]]))
