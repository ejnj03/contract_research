import json
import pandas as pd
from openai import OpenAI
import os
import re
from prompts.v1_single_prompt import context1, context2
from dataset import load_samples
#from pydantic import BaseModel

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])





def clean_json_string(json_string):
    pattern = r'.*?```json\s*(.*?)\s*```$'
    cleaned_string = re.sub(pattern, r'\1', json_string, flags=re.DOTALL)
    return cleaned_string.strip()

def load_existing_data(file_name):
    if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
        return pd.read_csv(file_name)
    else:
        return pd.DataFrame(columns=["citation", "disputed_word", "argument_position", "argument_type", "argument", "argument_excerpts", "contract_excerpt"])
        
def to_gpt_input(model, file_name1, file_name2):
    samples = load_samples()
    filenames = [(file_name1, context1), (file_name2, context2)]
    
    for file_name, context in filenames: 
        existing_data = load_existing_data(file_name)
        existing_citations = set(existing_data["citation"]) if not existing_data.empty else set()
        results = []
        
        for input_sample in samples:
            citation = input_sample["citation"]
            if citation in existing_citations:
                continue  # 이미 처리된 사례는 건너뜀
            
            if input_sample["text"] != "nan":
                messages = [
                        {"role": "user", "content": context.strip() + " citation: " + citation + ", " + input_sample["text"] + "\""},
                    ]
                
                print(f"Extracting response for {citation}")
                response = client.chat.completions.create(model=model, messages=messages)
                response_content = clean_json_string(response.choices[0].message.content)
                print(f"Writing response for {citation}")
                
                if response_content:
                    response_data = json.loads(response_content)
                    for item in response_data:
                        item["citation"] = citation
                        results.append(item)
                    
                    # 새로운 데이터를 기존 데이터와 합쳐서 저장
                    updated_df = pd.concat([existing_data, pd.DataFrame(results)], ignore_index=True)
                    updated_df.to_csv(file_name, index=False)
                    print(f"Saved response for {citation} to {file_name}")
                else:
                    print(f"No content for citation {citation}")
    
if __name__ == '__main__':
    to_gpt_input(model="o1-preview", file_name1='gpt_o1_version3_E_minibatch.csv', file_name2='gpt_o1_version_3_no_E.minibatch')
