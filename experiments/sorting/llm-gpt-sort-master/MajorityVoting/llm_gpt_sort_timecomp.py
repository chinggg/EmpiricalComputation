'''

 Runs the LLM sort and algorithmic sort on randomly generated lists and tracks the time taken
 Used to compare the timing of the LLM and algorithms in solving the sorting problem


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
EXPERIMENT_TAG = os.getenv("EXPERIMENT_TAG", "sort_timecomp")
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
        max_tokens=max_tokens, 
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

sampleRuns = 50

for ubound in range(105,125, 5):
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

                prompt_nums = f"""
                Sort the elements in the given collection in the {direction} order, and return only the sorted collection in the {collection_type} format:
                {to_sort}
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



                print(res)
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
        # print(f"\nOriginal sorted collection:\n{to_sort}")
        # print(f"\nLLM sorted collection:\n{sorted_list}")
        # print(f"\nAre these two list the same? {to_sort == sorted_list}")
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

with open(os.path.join(OUTDIR, "correctness.txt"), 'w+') as f:
        f.write(corrstr)
with open(os.path.join(OUTDIR, "sizes.txt"), 'w+') as f:
    f.write(sizestr)
with open(os.path.join(OUTDIR, "maxNum.txt"), 'w+') as f:
    f.write(maxnum)
with open(os.path.join(OUTDIR, "timeComp_API.txt"), 'w+') as f:
    f.write(timeAPI)
with open(os.path.join(OUTDIR, "timeCompJ_ALG.txt"), 'w+') as f:
    f.write(timeALG)
