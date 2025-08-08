'''
 Test whether majority voting will increase the LLMs accuracy on solving
 the sorting problem using randomly generated lists of increasing size,
 each sampled multiple times

'''
# code adapted from https://github.com/njmarko/llm-gpt-sort

import os
import openai
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file
import time
openai.api_key  = os.environ['OPENAI_API_KEY']

# Model and output configuration
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
MODEL_TAG = os.getenv("OPENAI_MODEL_TAG", MODEL_NAME.replace(":", "_").replace("/", "_"))
OUTPUT_ROOT = os.getenv("OUTPUT_ROOT", "output_models")
EXPERIMENT_TAG = os.getenv("EXPERIMENT_TAG", "sort_majority_voting")
OUTDIR = os.path.join(OUTPUT_ROOT, MODEL_TAG, EXPERIMENT_TAG)
os.makedirs(OUTDIR, exist_ok=True)


# In[2]:


def get_completion_from_messages(messages, 
                                 model=MODEL_NAME, 
                                 temperature=0, 
                                 max_tokens=1000):
    response = openai.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content


# # Generate a random list of numbers and sort it with GPT

# In[3]:


import random
import ast
import re



corrstr = ''
sizestr = ''
maxnum = ''
timeAPI = ''
timeALG = ''
doesMJmatter = ''
sampleRuns = 50

for ubound in range(55, 75, 5):
    size = ubound
    correctness = 0

    for i in range(sampleRuns):
        while True:
            try:
                to_sort =  random.sample(range(0, 1000), size)
                direction = 'Ascending'



                sys_msg = f"""
                Response should only contain the sorted data in the direction specified by the user.
                Do not say anything else, just return a same structure with the sorted information.
                You role is to only return the data.
                """

                collection_type = f"""
                list
                """

                prompt_nums = [f"""
                Sort the elements in the given collection in the {direction} order, and return only the sorted collection in the {collection_type} format:
                {to_sort}
                """,
                f"""
                double check and make sure that the size of the output is correct, Sort the elements in the given collection in the {direction} order, and return only the sorted collection in the {collection_type} format:
                {to_sort}
                """,
                f"""
                think step by step, Sort the elements in the given collection in the {direction} order, and return only the sorted collection in the {collection_type} format:
                {to_sort}
                """,

                f"""
                Sort the elements in the given collection in {direction} order, and return the sorted collection in the {collection_type} format:
                {to_sort}
                """,
                f"""
                think step by step, Sort the given collection in the {direction} order, and return only the sorted collection in the {collection_type} format:
                {to_sort}
                """,
                f"""
                Sort the elements in the given collection from least to greatest, and return only the sorted collection in the {collection_type} format:
                {to_sort}
                """,
                f"""
                Sort the elements in the given collection in the {direction} order, and return only the sorted collection in the {collection_type} format, ensuring not to miss any numbers:
                {to_sort}
                """,
                f"""
                Sort elements in the given collection from least to greatest, and return only the sorted collection in the {collection_type} format:
                {to_sort}
                """,
                f"""
                Sort the elements in the given list from least to greatest, and return only the sorted collection in the {collection_type} format:
                {to_sort}
                """,
                f"""
                Sort the numbers in the given collection from least to greatest, and return only the sorted collection in the {collection_type} format:
                {to_sort}
                """
                ]



                

                resdict = dict()
                start_timeAPI = time.time()
                for resSamples in range(10):
                    messages = [
                    {'role': 'system',
                    'content': sys_msg},
                    {'role':'user',
                    'content': prompt_nums[resSamples]}
                    ]
                    # print(messages)
                    res = get_completion_from_messages(messages)
                    if(res not in resdict):
                        resdict[res] = 1
                    else:
                        resdict[res] += 1
                    

                end_timeAPI = time.time()


                res = max(resdict, key = resdict.get)
                print(resdict)
                print(res)

                if(len(resdict) > 1):
                    doesMJmatter += 'True' + str(len(resdict)) + ': ' + str(resdict) + '\n'
                else:
                    doesMJmatter += 'False' + str(len(resdict)) + ': ' + str(resdict) + '\n'
                parsed_ok = False
                try:
                    sorted_list = ast.literal_eval(res)
                    parsed_ok = isinstance(sorted_list, list)
                except Exception:
                    parsed_ok = False
                if not parsed_ok and os.getenv("EVAL_NORMALIZE", "false").lower() in ("1", "true", "yes"):
                    m = re.search(r"\[[\s\S]*\]", res)
                    if m:
                        try:
                            sorted_list = ast.literal_eval(m.group(0))
                            parsed_ok = isinstance(sorted_list, list)
                        except Exception:
                            parsed_ok = False
                if not parsed_ok:
                    raise ValueError("Could not parse list response (strict or normalized)")
                break
            except Exception as ex:
                print("error: ")
                print(ex)


        # # Evaluation

        # In[4]:

        start_timeALG = time.time()
        to_sort.sort()
        end_timeALG = time.time()

        if(to_sort == sorted_list):
            correctness += 1
            corrstr+="1\n"
        else:
            corrstr+="0\n"
        sizestr += str(size) + '\n'
        timeAPI += str(end_timeAPI - start_timeAPI) + '\n'
        timeALG += str(end_timeALG - start_timeALG) + '\n'

        maxnum += str(ubound) + '\n'

    print(correctness, sampleRuns, correctness/sampleRuns)

with open(os.path.join(OUTDIR, "correctnessMJ_10_different_prompts.txt"), 'w+') as f:
        f.write(corrstr)
with open(os.path.join(OUTDIR, "sizesMJ_10_different_prompts.txt"), 'w+') as f:
    f.write(sizestr)
with open(os.path.join(OUTDIR, "maxNumMJ_10_different_prompts.txt"), 'w+') as f:
    f.write(maxnum)
with open(os.path.join(OUTDIR, "timeSortMJ_API_10_different_prompts.txt"), 'w+') as f:
    f.write(timeAPI)
with open(os.path.join(OUTDIR, "timeSortMJ_ALG_10_different_prompts.txt"), 'w+') as f:
    f.write(timeALG)
with open(os.path.join(OUTDIR, "MJ_matters_10_different_prompts.txt"), 'w+') as f:
    f.write(doesMJmatter)
