'''
 Test LLM accuracy on solving the subset sum problem by returning the subset 
 that sums to the goal using either randomly generated or LLM-generated
 sets of increasing sizes and solvable targets sampled multiple times each

'''
# code adapted from https://github.com/njmarko/llm-gpt-sort


import os
import openai
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
# Load repo-root .env if present (works from any CWD)
try:
    _env_path = None
    for _p in Path(__file__).resolve().parents:
        cand = _p / ".env"
        if cand.exists():
            _env_path = cand
            break
    if _env_path is not None:
        _ = load_dotenv(_env_path)
    else:
        _ = load_dotenv(find_dotenv())
except Exception:
    _ = load_dotenv(find_dotenv())
import time
import numpy as np
openai.api_key  = os.environ['OPENAI_API_KEY']

# Model and output configuration
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
MODEL_TAG = os.getenv("OPENAI_MODEL_TAG", MODEL_NAME.replace(":", "_").replace("/", "_"))
OUTPUT_ROOT = os.getenv("OUTPUT_ROOT", "output_models")
EXPERIMENT_TAG = os.getenv("EXPERIMENT_TAG", "subset_sum")
OUTDIR = os.path.join(OUTPUT_ROOT, MODEL_TAG, EXPERIMENT_TAG)
os.makedirs(OUTDIR, exist_ok=True)


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
def isSubsetSumEXP(totalset, target, index=0, current_subset=[]):

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
    incRes = isSubsetSumEXP(totalset, target - totalset[index], index + 1, current_subset + [totalset[index]])
    if(incRes != None):
         return incRes
    return isSubsetSumEXP(totalset, target, index + 1, current_subset)


def isValid(totalSet, goalVal, solved):
    goodans = True
    for x in solved:
        if x not in totalSet:
            goodans = False

    return(sum(solved) == goalVal and goodans)


def get_completion_from_messages(messages, 
                                 model=MODEL_NAME, 
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
from pathlib import Path

numsets = []
goalvals = []

# using the generated SSP instances; resolve relative to this script's directory
script_dir = Path(__file__).resolve().parent
ssp_input_path = script_dir / 'output' / 'generated_SSPs.txt'
with open(ssp_input_path, 'r') as file:
    # Read all lines into a list
    vals = file.read().splitlines()

for l in vals:

    numsetStr, goalStr = l.split('\t')

    numsets.append((ast.literal_eval(numsetStr), (int(goalStr))))




corrstr = ''
arrstr = ''
sizestr = ''
timeAPI = ''
timeALG = ''

sampleRuns = 1
validSets = []

# remove unsolvable instances
for (l, curgoal) in numsets:
    if(isSubsetSumEXP(l, curgoal) == None):

        print("invalid problem")

    else:
        validSets.append((l, curgoal))
numsets = validSets
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
                Do not say anything else, just return a list with the answer information.
                You role is to only return the data. Make sure the answer is correct.
                """

                collection_type = f"""
                list
                """

                prompt_nums = f"""
                According to the subset sum NP problem, return the elements that sum to {curgoal} from the set {to_solve} and return only the answer in the {collection_type} format. Think step by step.
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




            
                apiSol = ast.literal_eval(res)
                npcheck = np.array(apiSol)
                if not isinstance(apiSol, list) or npcheck.ndim != 1: 
                    raise Exception("bad response format")
                if len(apiSol) > 1 and isinstance(apiSol[1], list):
                    raise Exception("list within a list")
                break
            except Exception as ex:
                print("error: ")
                print(ex)
                errcount += 1


        # # Evaluation

        # In[4]:

        start_timeALG = time.time()
        algSolved = isSubsetSumEXP(l, curgoal)
        end_timeALG = time.time()
        print(algSolved, curgoal)
        
        if(not isValid(l, curgoal, algSolved)):
            raise Exception("algorithm validity issue")
        print(apiSol)
        print("res sum: " + str(sum(apiSol)))
        if(isValid(l, curgoal, apiSol)):
            correctness += 1
            corrstr+="1\n"
        else:
            corrstr+="0\n"
        sizestr += str(size) + '\n'
        timeAPI += str(end_timeAPI - start_timeAPI) + '\n'
        timeALG += str(end_timeALG - start_timeALG) + '\n'



    print(correctness, sampleRuns, correctness/sampleRuns)

with open(os.path.join(OUTDIR, "correctness.txt"), 'w+') as f:
    f.write(corrstr)
with open(os.path.join(OUTDIR, "sizes.txt"), 'w+') as f:
    f.write(sizestr)
with open(os.path.join(OUTDIR, "timeComp_API.txt"), 'w+') as f:
    f.write(timeAPI)
with open(os.path.join(OUTDIR, "timeCompJ_ALG.txt"), 'w+') as f:
    f.write(timeALG)
