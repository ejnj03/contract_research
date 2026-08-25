import json
import pandas as pd
from openai import OpenAI
import os
from script_text import part_1, part_2, part_3, part_4

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

#complete list of texts 
def format_csv():
    labels_df = pd.read_csv('labels.csv') 
    citations = labels_df['citation']
    text_list = labels_df['text'].to_list()
    citation_list = citations.to_list()
    label_list = labels_df['corrected_labels'].to_list()
    
    samples = [{"citation": citation, "text": str(text), "label": label} 
               for citation, text, label in zip(citation_list, text_list, label_list)]
    
    for sample in samples:
        if len(sample["text"]) <= 100:  # Corrected check for NaN
            file_path = f'data/{sample["citation"]}.txt'
            if os.path.exists(file_path):  # Ensure file exists before opening
                with open(file_path, 'r') as f:
                    text = f.read()
                    sample["text"] = text
    
    # Debugging output for entries that still have NaN text
    for _, input_sample in enumerate(samples):
        if len(sample["text"]) <= 100:  # Check for NaN text
            print(f"Missing text for citation: {input_sample['citation']}")
    
    return samples

def to_gpt_input(model, file_name, steps_file_name):
    samples = format_csv()
    with open(file_name, 'w') as f, open(steps_file_name, 'w') as f_s:
        for number, input_sample in enumerate(samples):
            if input_sample["text"] != "nan":
                content = "opinion_text = " + input_sample["text"]
                citation = input_sample["citation"]
                
                # Construct the message dictionary
                messages = [
                    {"role": "user", "content": part_1.strip() + content.strip()},
                    #{"role": "user", "content": question_7.strip()},
                ]
                
                # Construct the full JSON object
                print("extracting response 1...")
                response = client.chat.completions.create(model= model, messages= messages)
                print("writing response for " + citation + " step 1")
                message = "[START_1]" + citation + response.choices[0].message.content + "[END_1]"
                #other_messages = citation + response.choices[2].message.content + response.choices[1].message.content
                print(message)
                # Write the JSON object as a string to the file
                #f_s.write(json.dumps(message))
                messages.append({"role": "assistant", "content": response.choices[0].message.content})
                messages.append({"role": "user", "content": part_2.strip()})

                print("extracting response 2...")
                response = client.chat.completions.create(model= model, messages= messages)
                print("writing response for " + citation + " step 2")
                message = "[START_2]" + response.choices[0].message.content + "[END_2]"
                #other_messages = citation + response.choices[2].message.content + response.choices[1].message.content
                print(message)
                # Write the JSON object as a string to the file
                #f_s.write(json.dumps(message))
                messages.append({"role": "assistant", "content": response.choices[0].message.content})
                messages.append({"role": "user", "content": part_3.strip()})

                print("extracting response 3...")
                response = client.chat.completions.create(model= model, messages= messages)
                print("writing response for " + citation + " step 3")
                message = "[START_3]" + response.choices[0].message.content + "[END_3]"
                #other_messages = citation + response.choices[2].message.content + response.choices[1].message.content
                print(message)
                # Write the JSON object as a string to the file
                #f_s.write(json.dumps(messages))
                messages.append({"role": "assistant", "content": response.choices[0].message.content})
                messages.append({"role": "user", "content": part_4.strip()})
                f_s.write(citation + " " + json.dumps(messages))

                print("extracting final response...")
                response = client.chat.completions.create(model= model, messages= messages)
                print("writing response for " + citation + " step 4")
                message = citation + "[OUTPUT]" + response.choices[0].message.content
                #other_messages = citation + response.choices[2].message.content + response.choices[1].message.content
                print(message)
                # Write the JSON object as a string to the file
                f.write(json.dumps(message))

                #f_s.write(json.dumps())
                f_s.write('\n')
                f.write('\n')

if __name__ == '__main__':
    to_gpt_input(model="o1-preview", file_name='o1_structured_output_revised.jsonl', steps_file_name = 'o1_structured_output_revised_steps.jsonl')
