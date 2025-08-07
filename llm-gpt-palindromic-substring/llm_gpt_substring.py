'''
 Test LLM accuracy on solving the longest palindromic substring problem
 using randomly generated strings over increasing sizes sampled multiple times each

'''
# code adapted from https://github.com/njmarko/llm-gpt-sort

import os
import openai
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file
import time
openai.api_key  = os.environ['OPENAI_API_KEY']


# In[2]:




# There are multiple possible answers, so we will check the validity of the LLM's response
# by checking if it is a substring and the max length found.


def longestPalSubstr(s):
    n = len(s)
    start = 0
    end = 1

    for i in range(n):
        # Find the longest palindromic substring of even length
        low = i - 1
        hi = i

        while low >= 0 and hi < n and s[low] == s[hi]:
            if hi - low + 1 > end:
                start = low
                end = hi - low + 1
            low -= 1
            hi += 1

        # Find the longest palindromic substring of odd length
        low = i - 1
        hi = i + 1

        while low >= 0 and hi < n and s[low] == s[hi]:
            if hi - low + 1 > end:
                start = low
                end = hi - low + 1
            low -= 1
            hi += 1


    # Return the length of the longest palindromic substring
    return end



def isValid(testString, response):
    corrSize = longestPalSubstr(testString)
    isSub = response in testString
    return((len(response) == corrSize)  and (isSub))


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
import numpy as np
import string


corrstr = ''
sizestr = ''
maxnum = ''
timestr = ''
sampleRuns = 50
maxval = 1000

for ubound in range(1,21, 1):
    size = ubound
    correctness = 0
    errcount = 0

    for i in range(sampleRuns):
        while True:
            try:
                if(errcount > 5):
                    response = -123
                    break
                totalString = ''.join(random.choices(string.ascii_lowercase, k=size))




                sys_msg = f"""
                Response should only contain the data specified by the user.
                Do not say anything else, just return the answer.
                You role is to only return the answer.
                """


                prompt_nums = f"""
                Given the string [{totalString}], return the longest palindrome substring of the string
                without brackets. The substring must be a palindrome.
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

            
                response = res

                break
            except Exception as ex:
                print("error: ")
                print(ex)
                errcount += 1



        # # Evaluation

        # In[4]:


        algSol = longestPalSubstr(totalString)
        print(f"\nOriginal String:\n{totalString}")
        print(f"\nLLM answer:\n{response}")
        print(f"\ntrue answer len {algSol}")
        if(isValid(totalString, response)):
            correctness += 1
            corrstr+="1\n"
        else:
            corrstr+="0\n"
        sizestr += str(size) + '\n'
        timestr += str(end_time - start_time) + '\n'


    print(correctness, sampleRuns, correctness/sampleRuns)

with open("output/correctness.txt", 'w+') as f:
        f.write(corrstr)
with open("output/sizes.txt", 'w+') as f:
    f.write(sizestr)
with open("output/time.txt", 'w+') as f:
    f.write(timestr)


