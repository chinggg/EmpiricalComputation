'''
 Test LLM accuracy on solving the sorting problem by returning the sorted list
 using randomly generated lists of increasing size, each sampled multiple times

'''
# code adapted from https://github.com/njmarko/llm-gpt-sort

import os
import openai
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file
import time
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
# def get_completion_from_messages(messages, 
#                                  model="o1-preview", 
#                                  temperature=0):
#     response = openai.chat.completions.create(
#         model=model,
#         messages=messages,
#         temperature=temperature
#     )
#     return response.choices[0].message['content']

# # Generate a random list of numbers and sort it with GPT

# In[3]:


import random
import ast



corrstr = ''
sizestr = ''
maxnum = ''
timestr = ''
sampleRuns = 100

for ubound in range(10,60, 10):
    size = ubound
    correctness = 0

    for i in range(sampleRuns):
        while True:
            try:
                to_sort = random.sample(range(0, 1000), size)
                direction = 'Ascending'



                sys_msg = f"""
                Response should only contain the sorted data in the direction specified by the user.
                Do not say anything else, just return a structure with the sorted information.
                You role is to only return the data.
                """

                collection_type = f"""
                list
                """

                prompt_nums = f"""
                Sort the elements in the given collection in the {direction} order, and return only the sorted collection in the {collection_type} format:
                {to_sort}
                """

                # messages = [
                #     {'role':'user', 'content': prompt_nums}
                # ]

                messages = [
                    {'role': 'system',
                    'content': sys_msg},
                    {'role':'user',
                    'content': prompt_nums}
                ]

                start_time = time.time()

                res = get_completion_from_messages(messages)

                end_time = time.time()
                print(res)
            
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
        print(f"\nAre these two list the same? {to_sort == sorted_list}")
        if(to_sort == sorted_list):
            correctness += 1
            corrstr+="1\n"
        else:
            corrstr+="0\n"
        sizestr += str(size) + '\n'
        timestr += str(end_time - start_time) + '\n'

        maxnum += str(ubound) + '\n'

    print(correctness, sampleRuns, correctness/sampleRuns)

with open("output/correctness_100x.txt", 'w+') as f:
        f.write(corrstr)
with open("output/sizes_100x.txt", 'w+') as f:
    f.write(sizestr)
with open("output/maxNum_100x.txt", 'w+') as f:
    f.write(maxnum)
with open("output/timeSort_100x.txt", 'w+') as f:
    f.write(timestr)
