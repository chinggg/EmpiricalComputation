'''
Used to verify the timing behavior of linear search on randomly generated lists

'''
import random
import ast
import time



sizestr = ''

timestr = ''
sampleRuns = 1

maxsize = 100000000

maxrange = maxsize * 100

for ubound in [5, 10, 100, 1000, 10000, 100000, 1000000, 5000000, 7000000, 80000000, 90000000, 95000000, 97000000, 100000000]:
    print(ubound/maxsize)
    size = ubound
    correctness = 0

    for i in range(sampleRuns):
        ttestS = time.time()
        to_search = random.sample(range(0, maxrange), size)
        ttestM = time.time()
        target = random.sample(to_search, 1)[0]
        ttestE = time.time()
        print(9999991919919191)
        print(ttestM - ttestS)
        print(ttestE - ttestM)
        # # Evaluation

        # In[4]:

        start_time = time.time()
        # .index has O(n) complexity
        trueInd = to_search.index(target)
        end_time = time.time()


        sizestr += str(size) + '\n'
        timestr += str(end_time - start_time) + '\n'



with open("output/linsearch_sizes.txt", 'w+') as f:
    f.write(sizestr)

with open("output/linsearch_time.txt", 'w+') as f:
    f.write(timestr)