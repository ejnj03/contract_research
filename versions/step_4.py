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
    with open(file_name, 'w') as f, open(steps_file_name, 'r') as f_s:
        for number, input_sample in enumerate(samples):
            if input_sample["text"] != "nan":

                citation = input_sample["citation"]

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
