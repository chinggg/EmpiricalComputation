'''
Used to verify the timing behavior of n^2 solution to longest palindromic substring on randomly generated strings

'''


# code adapted from GeeksforGeeks

def longestPalSubstr(s):
    n = len(s)
    start = 0
    end = 1

    for i in range(n):
        # Find the longest palindromic substring of even length
        low = i - 1
        hi = i

        while low >= 0 and hi < n and s[low] == s[hi]:
            if hi - low + 1 > end:
                start = low
                end = hi - low + 1
            low -= 1
            hi += 1

        # Find the longest palindromic substring of odd length
        low = i - 1
        hi = i + 1

        while low >= 0 and hi < n and s[low] == s[hi]:
            if hi - low + 1 > end:
                start = low
                end = hi - low + 1
            low -= 1
            hi += 1


    return s[start:start + end]




import random
import ast
import numpy as np
import string
import time

sampleRuns = 1
timing = ''
timingE = ''
sizestr = ''

for size in range(6, 10007, 1000):
    for i in range(sampleRuns):
        totalString = ''.join(random.choices(string.ascii_lowercase, k=size//2))
        totalString = totalString + totalString[::-1]



        tstart = time.time()
        solved = longestPalSubstr(totalString)
        tend = time.time()



        sizestr += str((size//2) * 2) + '\n'

        timing += str(tend - tstart) + '\n'


with open("output/substr_sizes.txt", 'w+') as f:
    f.write(sizestr)

with open("output/substr_time.txt", 'w+') as f:
    f.write(timing)

