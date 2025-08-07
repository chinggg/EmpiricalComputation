'''
 Test LLM accuracy on solving the sorting problem on floating point numbers
 using randomly generated lists of floats with increasing number of decimals, each sampled multiple times

'''
# code adapted from https://github.com/njmarko/llm-gpt-sort

import os
import openai
import numpy as np
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

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


# # Generate a random list of numbers and sort it with GPT

# In[3]:


import random
import ast


sampleRuns = 50
arrsize = 50
corrstr = ''
sizestr = ''
for j in range(21):
    decimals = j
    correctness = 0

    for i in range(sampleRuns):

        while True:
            try:
                to_sort = np.around(np.random.uniform(0, 1000, size=(arrsize)), decimals).tolist()

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

                res = get_completion_from_messages(messages)


                sorted_list = ast.literal_eval(res)
                break
            except Exception as ex:
                print("error: ")
                print(ex)


                # # Evaluation

                # In[4]:


        to_sort.sort()
        print(f"\nOriginal sorted collection:\n{to_sort}")
        print(f"\nLLM sorted collection:\n{sorted_list}")
        print(f"\nAre these two list the same? {np.array_equal(to_sort, sorted_list)}")
        if(np.array_equal(to_sort, sorted_list)):
            correctness += 1
            corrstr+="1\n"
        else:
            corrstr+="0\n"
        sizestr += str(decimals) + '\n'
    print(correctness, sampleRuns, correctness/sampleRuns)



print(correctness, sampleRuns, correctness/sampleRuns)
with open("correctnessFloat.txt", 'w+') as f:
        f.write(corrstr)
with open("sizesFloat.txt", 'w+') as f:
    f.write(sizestr)
