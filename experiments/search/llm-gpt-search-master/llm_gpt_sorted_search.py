'''
 Test LLM accuracy on returning the index of a given integer in a sorted list
 using randomly generated lists of increasing sizes sampled multiple times each

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
EXPERIMENT_TAG = os.getenv("EXPERIMENT_TAG", "search_sorted")
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




# In[3]:


import random
import ast



corrstr = ''
sizestr = ''
maxnum = ''
timestr = ''
sampleRuns = 50

for ubound in range(5,155, 5):
    size = ubound
    correctness = 0
    errcount = 0

    for i in range(sampleRuns):
        while True:
            try:
                if(errcount > 5):
                    response = -123
                    break
                to_search = random.sample(range(0, 1000), size)
                to_search.sort()
                target = random.sample(to_search, 1)[0]



                sys_msg = f"""
                Response should only contain the data specified by the user.
                Do not say anything else, just return the correct index as an integer.
                You role is to only return the number.
                """


                prompt_nums = f"""
                Given a sorted list of numbers {to_search}, return the zero-based index of the number {target}
                in the list or -1 if the number isn't in the list.

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

            
                response = ast.literal_eval(res)
                break
            except Exception as ex:
                print("error: ")
                print(ex)
                errcount += 1



        # # Evaluation

        # In[4]:

        print(f"\nlist:\n{to_search}")
        print(f"\ntarget:\n{target}")
        trueInd = to_search.index(target)
        print(f"\nlist:\n{to_search}")
        print(f"\nLLM answer:\n{response}")
        print(f"\ntrue index {trueInd}")
        if(trueInd == response):
            correctness += 1
            corrstr+="1\n"
        else:
            corrstr+="0\n"
        sizestr += str(size) + '\n'
        timestr += str(end_time - start_time) + '\n'


    print(correctness, sampleRuns, correctness/sampleRuns)

with open(os.path.join(OUTDIR, "sorted_correctness.txt"), 'w+') as f:
        f.write(corrstr)
with open(os.path.join(OUTDIR, "sorted_sizes.txt"), 'w+') as f:
    f.write(sizestr)
with open(os.path.join(OUTDIR, "time.txt"), 'w+') as f:
    f.write(timestr)
