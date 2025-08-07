'''
Used to verify the timing behavior of sorting on randomly generated lists

'''
import random
import ast
import time
import numpy as np


sizestr = ''

timestr = ''
sampleRuns = 10

maxsize = 100000000

maxrange = maxsize * 100

pop_list = range(0, maxrange)

for ubound in [5, 10, 100, 1000, 10000, 100000, 1000000, 5000000, 7000000, 80000000, 90000000, 95000000, 97000000, 100000000]:
    print(ubound/maxsize)
    size = ubound
    correctness = 0

    for i in range(sampleRuns):
 

        ttestS = time.time()


        to_sort = random.sample(range(0, maxrange), size)

        ttestM = time.time()



        print(ttestM - ttestS)

        # # Evaluation

        # In[4]:

        start_time = time.time()
        to_sort.sort()
        end_time = time.time()



        sizestr += str(size) + '\n'
        timestr += str(end_time - start_time) + '\n'



with open("output/sort_sizes.txt", 'w+') as f:
    f.write(sizestr)

with open("output/sort_time.txt", 'w+') as f:
    f.write(timestr)