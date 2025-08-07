'''
 Finds the avergae lengths of the language representation of a randomly generated list of 
 integers
'''
# code adapted from https://github.com/njmarko/llm-gpt-sort

import os
import openai
import numpy as np

from pycnnum import num2cn
from num2words import num2words






lsize = ''
sampleRuns = 1000
for language in ['de']:
    def toapply(l):
        return num2words(l, lang=language)
    totalLen = 0

    for i in range(sampleRuns):

        to_sort = to_sort = np.random.randint(0, 1000, size=(30)).tolist()
        to_sort_cn = np.array([toapply(i) for i in to_sort])
        # # Evaluation

        # In[4]:


        sortedD = to_sort.sort()
        sortedD = np.copy(to_sort).tolist()
        to_sort = np.array([toapply(i) for i in to_sort]).tolist()
        print(f"\nOriginal sorted in decimals:\n{sortedD}")
        print(f"\nOriginal sorted collection:\n{to_sort}")


        for s in to_sort:
            totalLen += len(s)

    lsize += language + ': ' + str(totalLen / (sampleRuns * 30)) + '\n'


with open("avglen.txt", 'w+') as f:
    f.write(lsize)
