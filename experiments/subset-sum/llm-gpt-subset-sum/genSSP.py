'''
 Randomly generates instances of the SSP problem using
 sets of increasing sizes and solvable targets sampled multiple times each

'''

#  only generates solvable questions



import random
import ast
import numpy as np




# code adapted from GeeksforGeeks
def isSubsetSum(totalset, target, index=0, current_subset=[]):
    # print(index)
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
    incRes = isSubsetSum(totalset, target - totalset[index], index + 1, current_subset + [totalset[index]])
    if(incRes != None):
         return incRes
    return isSubsetSum(totalset, target, index + 1, current_subset)

def subsets(arr): 
    if(len(arr) == 0):
        return [[]]
    temp = subsets(arr[1:])
    augtemp = []
    for s in temp:
        augtemp.append([arr[0]] + s)
    # print(augtemp)
    return temp + augtemp


def isValid(totalSet, goalVal, solved):
    goodans = True
    for x in solved:
        if x not in totalSet:
            goodans = False

    return(sum(solved) == goalVal and goodans)


# unused function that could be used to generated unsolvable instances
def allSums(arr):
    allSubs = subsets(arr)
    allSums = []
    for s in allSubs:
        allSums.append(sum(s))
    return allSums
ssp = ''


sampleRuns = 20
maxval = 100

for sspSize in range(2, 16, 1):

    for i in range(sampleRuns):
        totalSet = np.random.choice(range(0, maxval), sspSize, replace=False)

        validGoals = sorted(allSums(totalSet))
        invalidGoals = set(range(validGoals[0], validGoals[-1] + 2)) - set(validGoals)

        print(invalidGoals)
        goalVal = np.random.choice(list(invalidGoals), 1)[0]
        ssp += str(totalSet.tolist()) + '\t' + str(goalVal) + '\n'


with open("output/generated_SSPs.txt", 'w+') as f:
        f.write(ssp)

