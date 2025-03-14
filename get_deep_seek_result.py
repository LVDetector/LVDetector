import os
from openai import OpenAI
from multiprocessing import Pool
import json
from tqdm import tqdm
import time

all_prompts='''
Analyze the given function to determine if it contains complete vulnerability semantic information according to the following criteria:
    1. **Vulnerable Functions** must contain:
        - At least one **bad source** (direct vulnerability-causing statement)
        - AND at least one **vulnerability-triggering statement**
    2 **Non-Vulnerable Functions** must satisfy either:
        - If containing **vulnerability-triggering statements**, must include:
            - **Good source** (safe alternative)
            - OR **sanitization operations**
        - If **no vulnerability-triggering statements**exist:
            - Must **not contain any bad source**
    Output format:
    { "is_complete": boolean, "rationale": string }
    Evaluate by strictly following these logical conditions. A function is considered semantically complete ONLY when it meets all requirements for its category (vulnerable/non-vulnerable). Highlight missing components or conflicting elements in your rationale.
'''
           

def get_single_result(param):
    filename,func_code,vul_type=param
    
    client = OpenAI(
        api_key="",  # how to get API Key：https://help.aliyun.com/zh/model-studio/developer-reference/get-api-key
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    user_prompt = all_prompts+"\n[function]:\n"+func_code
    while True:
        try:
            completion = client.chat.completions.create(
                model="deepseek-V2.5",  
                messages=[
                    {'role': 'user', 'content': user_prompt}
                ],
                # temperature=0.0
            )
        except Exception as e:
            print(e)
            time.sleep(60)
            continue
        break

    return {filename:str(completion.choices[0].message.content)}

if __name__ == '__main__':
    dir=r'D:\files\groundtruth\0'
    files=os.listdir(dir)
    params=[]
    final_dict={}
    for file in files[:5]:
        with open(os.path.join(dir,file),'r',encoding='utf-8') as f:
            function_code=f.read()
            params.append((file,function_code,"non_vul"))
    pbar=tqdm(total=len(params))
    with Pool(8) as p:
        results=p.imap_unordered(get_single_result,params)
        for result in results:
            final_dict.update(result)
            pbar.update(1)
    pbar.close()
    with open('non_vul_results_R1_t0.json','w',encoding='utf-8') as f:
        json.dump(final_dict,f,ensure_ascii=False,indent=4)

