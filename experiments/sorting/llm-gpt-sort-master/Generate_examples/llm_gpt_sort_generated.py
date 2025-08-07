'''
 Use the LLM to sort LLM-generated random lists of numbers.
 Used to find possible relation between familiarity and correctness

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



corrstr = ''
arrstr = ''
sizestr = ''

doesMJmatter = ''
sampleRuns = 1
sorted_lists = []

with open('output/generatedList.txt', 'r') as file:
    # Read all lines into a list
    vals = file.read().splitlines()

for l in vals:
    sorted_lists.append(ast.literal_eval(l))


for l in sorted_lists:
    for i in range(sampleRuns):
        sizestr += str(len(l)) + '\n'

with open("output/Gen_sizes.txt", 'w+') as f:
        f.write(sizestr)
for l in sorted_lists:
    correctness = 0

    permutated = l #no permutation

    for i in range(sampleRuns):
        errcount = 0
        while True:
            try:
                print('errcount')
                print(errcount)
                if(errcount >= 3):
                    sorted_list = []
                    break
                to_sort = permutated


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

                start_time = time.time()

                res = get_completion_from_messages(messages)

                end_time = time.time()
                print("res: " + res)
            
                sorted_list = ast.literal_eval(res)
                break
            except Exception as ex:
                print("error: ")
                print(ex)
                errcount += 1


        # # Evaluation

        # In[4]:


        to_sort = sorted(to_sort)

        if(to_sort == sorted_list):
            correctness += 1
            corrstr+="1\n"
        else:
            corrstr+="0\n"
        arrstr += str(l) + '\n'

    print(correctness, sampleRuns, correctness/sampleRuns)

with open("output/Gen_correctness.txt", 'w+') as f:
        f.write(corrstr)
with open("output/permutated_arrToSort.txt", 'w+') as f:
    f.write(arrstr)
