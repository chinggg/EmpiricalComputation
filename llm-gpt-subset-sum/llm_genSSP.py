'''
 Generates instances of the subset sum problem by prompting the LLM for
 sets of increasing sizes and solvable targets sampled multiple times each

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


resstr = ''
lastres = '[95, 12, 63, 28, 41, 77, 50, 3, 88, 19, 36, 72, 6, 55, 84, 33, 60, 14, 47, 22, 70, 9, 45, 81, 29, 66, 38, 93, 17, 52, 75, 1, 99, 24, 57, 44, 78, 31, 64]'

sampleRuns = 50

for i in range(sampleRuns):
    while True:
        try:
            direction = 'Ascending'



            sys_msg = f"""
            Response should only contain the data specified by the user.
            Do not say anything else, just return a list with the information.
            Your role is to only return the data.
            """
            prompt_nums = f"""
            return a random solvable instance of the subset sum problem with a random example set of length 6 and target goal as a space separated tuple. 
            Numbers in the set should be less than {str(100 + i)}
            """



            messages = [
                {'role': 'system',
                'content': sys_msg},
                {'role':'user',
                'content': prompt_nums}
            ]


            res = get_completion_from_messages(messages)
            lastres = res

                

            print(res)
            break

        except Exception as ex:
            print("error: ")
            print(ex)




    # print(f"\nLLM sorted collection:\n{sorted_list}")


    resstr += str(res) + '\n'



with open("output/llm_generated_SSPs.txt", 'w+') as f:
        f.write(resstr)

