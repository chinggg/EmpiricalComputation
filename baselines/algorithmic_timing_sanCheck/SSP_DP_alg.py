'''
Used to verify the timing behavior of DP solution to subset sum problem on
randomly generated sets and reachable goals

'''





import random
import ast
import time
import numpy as np




# code from GeeksforGeeks
def isSubsetSumDP(set, target):
    n = len(set)

    # The value of subset[i][j] will be
    # true if there is a
    # subset of set[0..j-1] with sum equal to i
    subset = ([[False for i in range(target + 1)]
               for i in range(n + 1)])

    # If target is 0, then answer is true
    for i in range(n + 1):
        subset[i][0] = True

    # If target is not 0 and set is empty,
    # then answer is false
    for i in range(1, target + 1):
        subset[0][i] = False

    # Fill the subset table in bottom up manner
    for i in range(1, n + 1):
        for j in range(1, target + 1):
            if j < set[i-1]:
                subset[i][j] = subset[i-1][j]
            if j >= set[i-1]:
                subset[i][j] = (subset[i-1][j] or
                                subset[i - 1][j-set[i-1]])
                
    if not subset[n][target]:
        return []
    
    # To find the subset, we backtrack from dp[n][target]
    sol = []
    i, j = n, target
    while i > 0 and j > 0:
        if subset[i][j] and not subset[i-1][j]:
            sol.append(set[i-1])
            j -= set[i-1]
        i -= 1
    
    return sol[::-1]




# code adapted from GeeksforGeeks
# can be used if testing exponential solution
def isSubsetSumExp(totalset, target, index=0, current_subset=[]):

    # Base Cases
    if (target == 0):
        return current_subset
    if (index >= len(totalset)):
        return None
    if (target < 0):
        return None

    # Else, check if target can be obtained
    # by any of the following
    # (a) including the last element
    # (b) excluding the last element
    incRes = isSubsetSumExp(totalset, target - totalset[index], index + 1, current_subset + [totalset[index]])
    if(incRes != None):
         return incRes
    return isSubsetSumExp(totalset, target, index + 1, current_subset)



sampleRuns = 10
maxval = 100000
timing = ''
timingE = ''
sizestr = ''

for sspSize in range(55, 65, 5):
    for i in range(sampleRuns):
        print(sspSize)
        totalSet = np.random.choice(range(0, maxval), sspSize, replace=False)
        answerSize = random.sample(range(1, sspSize + 1), 1)    #how many number are in the answer set
        answerSet = np.random.choice(totalSet, answerSize, replace=False)
        goalVal = np.sum(answerSet)

        tstart = time.time()
        solved = isSubsetSumDP(totalSet.tolist(), goalVal)
        tend = time.time()


        sizestr += str(sspSize) + '\n'

        timing += str(tend - tstart) + '\n'



with open("output/SSP_DP_sizes.txt", 'w+') as f:
    f.write(sizestr)

with open("output/time_DP.txt", 'w+') as f:
    f.write(timing)

