import json
import pandas as pd
from openai import OpenAI
import os
from script_text_variant import part_1, part_2, part_3, part_4
import csv
import ast


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

def append_to_file(file_path, citation, model, input_step, input_for_step):
    new_entry = [citation, model, input_step, input_for_step]
    with open(file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(new_entry)
        file.close()

def check_exists(file_path, citation, model, input_step):
    df = pd.read_csv(file_path, quotechar='"', quoting=csv.QUOTE_MINIMAL)
    condition = (df['citation'] == citation) & (df['model'] == model) & (df['response_number'] == input_step)
    filtered_df = df[condition]
    if not filtered_df.empty:
        model_response = ast.literal_eval(filtered_df['response'].iloc[0])
        if input_step == "second_input": 
            if part_2 != model_response[2]["content"]:
                model_response[2]['content'] = part_2
                #update df
                df.loc[condition, 'response'] = str(model_response)
                df.to_csv(file_path, index=False)
                print("Updated second prompt in storage_dict")
        if input_step == "third_input": 
            if part_3 != model_response[2]["content"]:
                model_response[2]['content'] = part_3
                #update df
                df.loc[condition, 'response'] = str(model_response)
                df.to_csv(file_path, index=False)
                print("Updated third prompt in storage_dict")
        if input_step == "fourth_input": 
            if part_4 != model_response[2]["content"]:
                model_response[2]['content'] = part_4
                #update df
                df.loc[condition, 'response'] = str(model_response)
                df.to_csv(file_path, index=False)
                print("Updated fourth prompt in storage_dict")
    else: 
        model_response = None
    return model_response

def check_exists_output(file_path, citation, model):
    df = pd.read_csv(file_path, quotechar='"', quoting=csv.QUOTE_MINIMAL)
    filtered_df = df[(df['citation'] == citation) & (df['model'] == model)]
    if not filtered_df.empty:
        return True
    else: 
        return False

def to_gpt_input(model, file_name, steps_file_name):
    samples = format_csv()
    for number, input_sample in enumerate(samples):
        if input_sample["text"] != "nan":
            content = " This the the opinion text: opinion_text = " + input_sample["text"]
            citation = input_sample["citation"]
            
            # Construct the message dictionary
            messages = [
                {"role": "user", "content": part_1.strip() + content.strip()},
                #{"role": "user", "content": question_7.strip()},
            ]
            
            #create prompt for step 2 by using archived prompt/ obtaining response for Step 1
            step_2_input = check_exists(steps_file_name, citation, model, "second_input")
            if step_2_input == None:
            # Construct the full JSON object
                print("extracting response 1...")
                response = client.chat.completions.create(model= model, messages= messages)
                print("writing response for " + citation + " step 1")
                message = "[START_1]" + citation + response.choices[0].message.content + "[END_1]"
                #other_messages = citation + response.choices[2].message.content + response.choices[1].message.content
                print(message)
                # Write the JSON object as a string to the file
                #f_s.write(json.dumps(message))
                revised_first_prompt =  r'Identify and provide in your response motions, a set of specific occasions (procedural actions) and the motivating party (the party that filed the procedural action) that the court issues a decision on in opinion_text, and issues, a dictionary mapping motions to a set of issues that the court identifies as key to the making a judgment on the motion, extracted directly from the opinion_text (motion: Set(issues on the motion) for every motion in motions).' + content.strip()
                messages = [{"role": "user", "content": revised_first_prompt}]
                messages.append({"role": "assistant", "content": response.choices[0].message.content})
                messages.append({"role": "user", "content": part_2.strip()})
                append_to_file(steps_file_name, citation, model, "second_input", messages)
            else:
                print("Using pre-existing input for step 2 of " + citation)
                messages = step_2_input

            #create prompt for step 3 by using archived prompt/ obtaining response for Step 2 
            step_3_input = check_exists(steps_file_name, citation, model, "third_input")
            if step_3_input == None:
                print("extracting response 2...")
                #here we use the messages for step 2 obtained in the block above
                response = client.chat.completions.create(model= model, messages= messages)
                print("writing response for " + citation + " step 2")
                message = "[START_2]" + response.choices[0].message.content + "[END_2]"
                #other_messages = citation + response.choices[2].message.content + response.choices[1].message.content
                print(message)
                # Write the JSON object as a string to the file
                #f_s.write(json.dumps(message))
                revised_second_prompt = r'Identify and provide updated_issues_dict, a dictionary with key as issue/burden of proof i, and value as the set of sub-issue(s) (issue(s)/burden of proof(s) that i is contingent upon. This is essentially an adjacency list representation of trees, one tree for each major issue in the opinion_text, where each of these major issues would be the root node of the respective trees. Then, identify and provide the leaf nodes of all trees as elements of the set leaves.' + content.strip()
                messages = [{"role": "user", "content": revised_second_prompt}]
                messages.append({"role": "assistant", "content": response.choices[0].message.content})
                messages.append({"role": "user", "content": part_3.strip()})
                append_to_file(steps_file_name, citation, model, "third_input", messages)
            else:
                print("Using pre-existing input for step 3 of " + citation)
                messages = step_3_input

            #create prompt for step 4 by using archived prompt/ obtaining response for Step 3
            #For step 4, check_exists modifies archived prompt when assigning to step_4_input
            step_4_input = check_exists(steps_file_name, citation, model, "fourth_input")
            if step_4_input == None:
                print("extracting response 3...")
                response = client.chat.completions.create(model= model, messages= messages)
                print("writing response for " + citation + " step 3")
                message = "[START_3]" + response.choices[0].message.content + "[END_3]"
                #other_messages = citation + response.choices[2].message.content + response.choices[1].message.content
                print(message)
                # Write the JSON object as a string to the file
                #f_s.write(json.dumps(messages))
                revised_third_prompt = r'Provide a nested dictionary that has a key corresponding to each issue i in the opinion_text that the defendant and plaintiff directly dispute over, and value as a dictionary with keys “defendant” and “plaintiff”; Each respective value for actor a should correspond to a edge-labeled directed graph (tree) represented as a set of tuples (parent, relation, child), where parent would correspond to the position that a (the actor that is specified as the key of this entry) takes on the issue i, relation (either “support” or “refutations”), and child the set of supporting claims made by actor a in support of the parent claim if relation is “\support\”, or the set of refutations made against the parent claim if relation is “refutations.”' +  content.strip()
                messages = [{"role": "user", "content": revised_third_prompt}]
                messages.append({"role": "assistant", "content": response.choices[0].message.content})
                messages.append({"role": "user", "content": part_4.strip()})
                #print(part_4)
                append_to_file(steps_file_name, citation, model, "fourth_input", messages)
                #f_s.write(citation + " " + json.dumps(messages))
            else: 
                print("Using pre-existing input for step 4 of " + citation)
                messages = step_4_input


            if check_exists_output(file_name, citation, model):
                print("Output already exists for " + citation)
                continue
            else:
                print("extracting final response...")
                response = client.chat.completions.create(model= model, messages= messages)
                print("writing response for " + citation + " step 4")
                message = citation + "[OUTPUT]" + response.choices[0].message.content
                #other_messages = citation + response.choices[2].message.content + response.choices[1].message.content
                print(message)
                # Write the JSON object as a string to the file
                with open(file_name, 'a', newline='') as f:
                    writer = csv.writer(f)
                    new_response = [citation, model, message]
                    writer.writerow(new_response)
                    f.close()

            #f_s.write(json.dumps())

if __name__ == '__main__':
    to_gpt_input(model="o1-preview", file_name='response_4.csv', steps_file_name = 'storage_dict.csv')
