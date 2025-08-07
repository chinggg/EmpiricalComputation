'''
 Use the LLM to generate some numbers. Used to find possible relation between familiarity
 and correctness

'''
# code adapted from https://github.com/njmarko/llm-gpt-sort



import os
import openai
import numpy as np
from dotenv import load_dotenv, find_dotenv
from pycnnum import num2cn
from num2words import num2words

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





corrstr = ''
sizestr = ''
sampleSize = 5000
res_list = []
while True:
    try:
# print(to_sort)
        maxV = '1000000000'

        collection_type = f"""
        list
        """

        sys_msg = f"""
        Response should only contain the data in the range specified by the user.
        Do not say anything else, just return a {collection_type} with the randomly generated {sampleSize} numbers data and nothing else. Do not use ellipses.
        You role is to only return the data.
        """

        

        prompt_nums = f"""
        randomly generate {sampleSize} numbers in the range 0 to {maxV}, and return only the collection in the {collection_type} format. make sure to randomly generate exactly generate {sampleSize} numbers.
        """



        messages = [
    {'role': 'system',
    'content': sys_msg},
    {'role':'user',
    'content': prompt_nums}
]


# print(res)

    
        
        res = get_completion_from_messages(messages)
        print(res)
        res_list = ast.literal_eval(res)
        break
    except Exception as ex:
        print("error: ")
        print(ex)

        with open("gen_error.txt", 'w+') as f:
            f.write(res)
        break;


# # Evaluation

# In[4]:



print(f"\nLLM sorted collection:\n{res_list}")

sizestr += str(res_list) + '\n'



with open("genNums.txt", 'w+') as f:
        f.write(sizestr)

