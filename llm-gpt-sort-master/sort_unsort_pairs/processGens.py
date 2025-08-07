import pingouin as pg
import numpy as np
from scipy.stats import mannwhitneyu
import ast

with open('output/generatedpairs.txt', 'r') as file:
    # Read all lines into a list
    pairs = file.read().split('\n\n')

resp = ''
sizestr = ''
for pair in pairs:
    print(pair)
    unsort, sort = pair.split('\n')
    unsort = ast.literal_eval(unsort)
    cursize = len(unsort)
    sort = ast.literal_eval(sort)
    
    if(sorted(unsort) != sort):
        print('wrong:\n')
        print(sorted(unsort))
        print(sort)
        resp += '0\n'
    else:
        print('true\n')
        resp += '1\n'
    sizestr += str(cursize) + '\n'
    

with open("output/correctness_gpairs.txt", 'w+') as f:
        f.write(resp)
with open("output/size_gpairs.txt", 'w+') as f:
        f.write(sizestr)