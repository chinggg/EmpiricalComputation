'''
 Remove improperly formatted llm responses for generating lists to sort
'''
# code adapted from https://github.com/njmarko/llm-gpt-sort



import pingouin as pg
import numpy as np
from scipy.stats import mannwhitneyu

with open('output/generatedList.txt', 'r') as file:
    # Read all lines into a list
    vals = file.read().splitlines()

track = dict()
for f in vals:
    if('.' not in f and (not f.isdecimal())):
        continue
    print(f)
    if('.' not in f):
        deci = ''
    else:
        _, deci = f.split('.')
    
    if len(deci) not in track:
        track[len(deci)] = 1
    else:
        track[len(deci)] += 1

print(track)
