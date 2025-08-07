'''
Used to verify the timing behavior of binary search on randomly generated lists

'''
import random
import ast
import time


# code adapted from GeeksforGeeks
def binary_search(arr, x):
    low = 0
    high = len(arr) - 1
    mid = 0
 
    while low <= high:
 
        mid = (high + low) // 2
 
        # If x is greater, ignore left half
        if arr[mid] < x:
            low = mid + 1
 
        # If x is smaller, ignore right half
        elif arr[mid] > x:
            high = mid - 1
 
        # means x is present at mid
        else:
            return mid
 
    # If we reach here, then the element was not present
    return -1

sizestr = ''

timestr = ''
sampleRuns = 10

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

        to_search.sort()

        target = random.sample(to_search, 1)[0]
        ttestE = time.time()

        print(9999991919919191)
        print(ttestM - ttestS)
        print(ttestE - ttestM)
        # # Evaluation

        # In[4]:

        start_time = time.time()
        # to_sort.sort()
        # .index has O(n) complexity
        trueInd = binary_search(to_search, target)
        end_time = time.time()


        sizestr += str(size) + '\n'
        timestr += str(end_time - start_time) + '\n'



with open("output/bisearch_sizes.txt", 'w+') as f:
    f.write(sizestr)

with open("output/bisearch_time.txt", 'w+') as f:
    f.write(timestr)