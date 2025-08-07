'''
 Test LLM accuracy on solving the sorting problem on language representation of integers
 using randomly generated lists of increasing size translated into various languages,
each sampled multiple times
'''
# code adapted from https://github.com/njmarko/llm-gpt-sort


import os
import openai
import numpy as np
from dotenv import load_dotenv, find_dotenv
from pycnnum import num2cn
from num2words import num2words
import time

_ = load_dotenv(find_dotenv()) # read local .env file

openai.api_key  = os.environ['OPENAI_API_KEY']

# Model and output configuration
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
MODEL_TAG = os.getenv("OPENAI_MODEL_TAG", MODEL_NAME.replace(":", "_").replace("/", "_"))
OUTPUT_ROOT = os.getenv("OUTPUT_ROOT", "output_models")
EXPERIMENT_TAG = os.getenv("EXPERIMENT_TAG", "sort_language")
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


language = 'fr'
def toapply(l):
    return num2words(l, lang=language)


corrstr = ''
sizestr = ''
timestr = ''
sampleRuns = 30
for arrlen in range(5, 21, 5):
    size = arrlen
    correctness = 0

    for i in range(sampleRuns):

        while True:
            try:

                direction = 'Ascending'

                to_sort = np.random.randint(0, 1000, size=(arrlen)).tolist()
                to_sort_cn = np.array([toapply(i) for i in to_sort])


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
                {to_sort_cn}
                """



                messages = [
                    {'role': 'system',
                    'content': sys_msg},
                    {'role':'user',
                    'content': prompt_nums}
                ]

        

        
            
                start_time = time.time()

                res = get_completion_from_messages(messages)

                end_time = time.time()

                sorted_list = ast.literal_eval(res)
                break
            except Exception as ex:
                print("error: ")
                print(ex)


        # # Evaluation

        # In[4]:


        sortedD = to_sort.sort()
        sortedD = np.copy(to_sort).tolist()
        to_sort = np.array([toapply(i) for i in to_sort]).tolist()
        print(f"\nOriginal sorted in decimals:\n{sortedD}")
        print(f"\nOriginal sorted collection:\n{to_sort}")
        print(f"\nLLM sorted collection:\n{sorted_list}")
        print(f"\nAre these two list the same? {np.array_equal(to_sort, sorted_list)}")
        if(np.array_equal(to_sort, sorted_list)):
            correctness += 1
            corrstr+="1\n"
        else:
            corrstr+="0\n"
        sizestr += str(arrlen) + '\n'
        timestr += str(end_time - start_time) + '\n'
    print(correctness, sampleRuns, correctness/sampleRuns)



print(correctness, sampleRuns, correctness/sampleRuns)
with open(os.path.join(OUTDIR, "correctnessLang.txt"), 'w+') as f:
    f.write(corrstr)
with open(os.path.join(OUTDIR, "sizesLang.txt"), 'w+') as f:
    f.write(sizestr)
with open(os.path.join(OUTDIR, "timeLang.txt"), 'w+') as f:
    f.write(timestr)
