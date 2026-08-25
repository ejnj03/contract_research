import vertexai
from vertexai.preview.generative_models import GenerativeModel, ChatSession


import json
import pandas as pd
from gpt_batch_process import batch_process
from openai import OpenAI
import os
import re
import csv
from time import sleep

#os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./Authentication.json"

PROJECT_ID = "autonomous-star-413714"
vertexai.init(project=PROJECT_ID, location="us-central1")

model = GenerativeModel("gemini-1.5-flash-001")

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


context = "You are a careful law student who is skilled at identifying logical structures within legal documents and uses step by step reasoning. The pasted text is the full text of the opinion of a court case about contract disputes. Please answer following questions about this case based on the opinion, and format answers as the number and question followed by the answer. Answers do not have to be in complete sentences."

question_1 = "1. A case that is a contract language interpretation dispute is one where the plaintiff and defendant assert different interpretations of a phrase or term in a contract or argue about whether a phrase or term in a contract is ambiguous and subject to interpretation. Based on this definition, is this case about language interpretation dispute? Answer '1' if it is a contract language interpretation dispute and '0' otherwise."
question_2 = "2. What's the specific word or phrase in the contract that the plaintiff and defendant dispute over? It may be the case that the term or phrase (we call this phrase A) is defined explicitly in the contract, so the dispute is over the interpretation of another term or phrase (we reference this as phrase B) within the part of the contract that defines phrase A. In this case, include only phrase B." 
question_3 = "3. What is the contract excerpt that the disputed phrase or term occurs in? If the answer to the previous question includes two or more terms or phrases, include contract excerpts relevant to both terms or phrases."
question_4 = "4. What's the plaintiff's interpretation of the disputed contract language that was the answer to question 2?"
question_5 = "5. What's the defendant's interpretation of the disputed contract language that was the answer to question 2?"
question_6 = "6. Who did the court side with, and why? Answer 'P' if plaintiff and 'D' if defendant."

question_list = [question_1, question_2, question_3, question_4, question_5, question_6]
def chat_session(opinion_text, file, citation):
    chat = model.start_chat(response_validation=False)
    with open(file, "a") as f:
        chat.send_message(context + opinion_text)
        #responses.append(chat.send_message(question_2))
        #responses.append(chat.send_message(question_3))
        #responses.append(chat.send_message(question_4))
        #responses.append(chat.send_message(question_5))
        #responses.append(chat.send_message(question_6))
        f.write(r'{' + citation + r'}, ')
        for question in question_list:
            f.write(r'{')
            response = chat.send_message(question, stream=True)
            for chunk in response:
                text = chunk.text.strip()
                f.write(text)
                print(text)
            f.write(r'}')
            f.write(", ")
            sleep(30)
        f.write("\n")
    f.close()

def process(file):
    samples = format_csv()
    #print(samples[0])
    for input_sample in samples[5:]:
        chat_session(input_sample["text"], file, input_sample["citation"])
        sleep(30)
        

if __name__ == "__main__":
    process('gemini_output.jsonl')

