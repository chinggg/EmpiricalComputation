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
                sorted_list = ast.literal_eval(res)
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

with open("output/correctnessMJ_10_different_prompts.txt", 'w+') as f:
        f.write(corrstr)
with open("output/sizesMJ_10_different_prompts.txt", 'w+') as f:
    f.write(sizestr)
with open("output/maxNumMJ_10_different_prompts.txt", 'w+') as f:
    f.write(maxnum)
with open("output/timeSortMJ_API_10_different_prompts.txt", 'w+') as f:
    f.write(timeAPI)
with open("output/timeSortMJ_ALG_10_different_prompts.txt", 'w+') as f:
    f.write(timeALG)
with open("output/MJ_matters_10_different_prompts.txt", 'w+') as f:
    f.write(doesMJmatter)
