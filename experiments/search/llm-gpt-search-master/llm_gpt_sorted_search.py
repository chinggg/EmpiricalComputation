'''
 Test LLM accuracy on returning the index of a given integer in a sorted list
 using randomly generated lists of increasing sizes sampled multiple times each

'''
# code adapted from https://github.com/njmarko/llm-gpt-sort

import os
import openai
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
# Load repo-root .env if present (works from any CWD)
try:
    _env_path = None
    for _p in Path(__file__).resolve().parents:
        cand = _p / ".env"
        if cand.exists():
            _env_path = cand
            break
    if _env_path is not None:
        _ = load_dotenv(_env_path)
    else:
        _ = load_dotenv(find_dotenv())
except Exception:
    _ = load_dotenv(find_dotenv())
import time
openai.api_key  = os.environ['OPENAI_API_KEY']

# Model and output configuration
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
MODEL_TAG = os.getenv("OPENAI_MODEL_TAG", MODEL_NAME.replace(":", "_").replace("/", "_"))
OUTPUT_ROOT = os.getenv("OUTPUT_ROOT", "output_models")
EXPERIMENT_TAG = os.getenv("EXPERIMENT_TAG", "search_sorted")
OUTDIR = os.path.join(OUTPUT_ROOT, MODEL_TAG, EXPERIMENT_TAG)
os.makedirs(OUTDIR, exist_ok=True)
EVAL_NORMALIZE = os.getenv("EVAL_NORMALIZE", "false").lower() in ("1", "true", "yes")


# In[2]:


def get_completion_from_messages(messages, 
                                 model=MODEL_NAME, 
                                 temperature=0, 
                                 max_tokens=1000):
    response = openai.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content




# In[3]:


import random
import ast
import re



corrstr = ''
sizestr = ''
maxnum = ''
timestr = ''
sampleRuns = 50
if EVAL_NORMALIZE:
    corrstr_norm = ''

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

            
                # Strict parse
                strict_ok = False
                try:
                    response = ast.literal_eval(res)
                    strict_ok = isinstance(response, int)
                except Exception:
                    strict_ok = False
                # Normalized parse (optional)
                normalized_value = None
                if EVAL_NORMALIZE:
                    m = re.search(r"-?\d+", res)
                    if m:
                        try:
                            normalized_value = int(m.group(0))
                        except Exception:
                            normalized_value = None
                # If neither strict nor normalized worked, throw to retry
                if not strict_ok and not (EVAL_NORMALIZE and normalized_value is not None):
                    raise ValueError("Could not parse integer response (strict or normalized)")
                # Prefer strict for evaluation; keep normalized for secondary metric
                if strict_ok:
                    response_int = response
                else:
                    response_int = normalized_value
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
        print(f"\nLLM answer:\n{response_int}")
        print(f"\ntrue index {trueInd}")
        if(trueInd == response_int):
            correctness += 1
            corrstr+="1\n"
        else:
            corrstr+="0\n"
        sizestr += str(size) + '\n'
        timestr += str(end_time - start_time) + '\n'
        if EVAL_NORMALIZE:
            # If strict failed but normalized succeeded, then response_int already reflects normalized
            # For normalized metric, compare normalized_value (fallback to strict if available)
            norm_val = response_int if normalized_value is None else normalized_value
            corrstr_norm += ("1\n" if trueInd == norm_val else "0\n")


    print(correctness, sampleRuns, correctness/sampleRuns)

with open(os.path.join(OUTDIR, "sorted_correctness.txt"), 'w+') as f:
        f.write(corrstr)
with open(os.path.join(OUTDIR, "sorted_sizes.txt"), 'w+') as f:
    f.write(sizestr)
with open(os.path.join(OUTDIR, "time.txt"), 'w+') as f:
    f.write(timestr)
if EVAL_NORMALIZE:
    with open(os.path.join(OUTDIR, "sorted_correctness_normalized.txt"), 'w+') as f:
        f.write(corrstr_norm)
