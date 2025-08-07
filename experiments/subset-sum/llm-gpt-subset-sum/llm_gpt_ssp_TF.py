'''
 Unused file.

 Test LLM accuracy on solving the subset sum problem by returning solvability 
of either randomly generated or LLM-generated instances of the Subset sum problem


'''
# code adapted from https://github.com/njmarko/llm-gpt-sort

import os
import openai
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file
import time
import numpy as np
openai.api_key  = os.environ['OPENAI_API_KEY']


# In[2]:

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
def isSubsetSum(totalset, target, index=0):
    # print(index)
    # Base Cases
    if (target == 0):
        return True
    if (index >= len(totalset)):
        return False
    if (target < 0):
        return False

    # Else, check if target can be obtained
    # by any of the following
    # (a) including the last element
    # (b) excluding the last element
    incRes = isSubsetSum(totalset, target - totalset[index], index + 1)
    if(incRes != False):
         return incRes
    return isSubsetSum(totalset, target, index + 1)


def isValid(totalSet, goalVal, solved):
    goodans = True
    for x in solved:
        if x not in totalSet:
            goodans = False

    return(sum(solved) == goalVal and goodans)


def get_completion_from_messages(messages, 
                                 model="gpt-3.5-turbo", 
                                 temperature=0, 
                                 max_tokens=1000):
    response = openai.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature, 
        max_tokens=max_tokens, 
    )
    return response.choices[0].message.content




# In[3]:


import random
import ast

numsets = []
goalvals = []
with open('output/generated_SSPs.txt', 'r') as file:
    # Read all lines into a list
    vals = file.read().splitlines()

for l in vals:

    numsetStr, goalStr = l.split('\t')

    numsets.append((ast.literal_eval(numsetStr), (int(goalStr))))

print(numsets)





corrstr = ''
arrstr = ''
sizestr = ''
timeAPI = ''
timeALG = ''

sampleRuns = 1
for (l, curgoal) in numsets:
    if(isSubsetSum(l, curgoal) == None):
        # raise Exception("invalid problem")
        print("invalid problem")

for (l, curgoal) in numsets:
    size = len(l)
    correctness = 0
    errcount = 0
    for i in range(sampleRuns):
        while True:
            try:
                if(errcount > 5):
                    apiSol = []
                    break
                to_solve =  l



                sys_msg = f"""
                Response should only contain the data specified by the user obtained by solving the subset sum problem.
                Do not say anything else, just return True or False.
                You role is to only return the data. Make sure the answer is correct.
                """

                collection_type = f"""
                list
                """

                prompt_nums = f"""
                According to the subset sum NP problem, is it solvable given target {curgoal} and the set {to_solve}? return only the answer as True or False. Think step by step.
                Double check the answer.
                """




                messages = [
                    {'role': 'system',
                    'content': sys_msg},
                    {'role':'user',
                    'content': prompt_nums}
                ]

                resdict = dict()
                start_timeAPI = time.time()

                res = get_completion_from_messages(messages)

                    

                end_timeAPI = time.time()


                print(to_solve)
                print(res)
            
                apiSol = ast.literal_eval(res)

                break

            except Exception as ex:
                print("error: ")
                print(ex)
                errcount += 1


        # # Evaluation

        # In[4]:

        start_timeALG = time.time()
        algSolved = isSubsetSum(l, curgoal)
        end_timeALG = time.time()
        print(algSolved, curgoal)

        print(apiSol)
        if(apiSol == algSolved):
            correctness += 1
            corrstr+="1\n"
        else:
            corrstr+="0\n"
        sizestr += str(size) + '\n'
        timeAPI += str(end_timeAPI - start_timeAPI) + '\n'
        timeALG += str(end_timeALG - start_timeALG) + '\n'



    print(correctness, sampleRuns, correctness/sampleRuns)

with open("output/correctness.txt", 'w+') as f:
    f.write(corrstr)
with open("output/sizes.txt", 'w+') as f:
    f.write(sizestr)
with open("output/timeComp_API.txt", 'w+') as f:
    f.write(timeAPI)
with open("output/timeCompJ_ALG.txt", 'w+') as f:
    f.write(timeALG)
