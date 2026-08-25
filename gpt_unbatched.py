import json
import pandas as pd
from openai import OpenAI
import os
import re
#from pydantic import BaseModel

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



context1 = """1. Identify and define Contract to be the legal definition given in the opinion_text; If it is not explicitly provided, a document should be considered a contract
   if the court in the opinion_text deems the document as legally binding.

   2. Define a Locus as (a segment of word(s) that are either: {a single word (example: discuss)} OR {single
   grammatical phrase (noun phrase, verb phrase, adjective phrase, etc.) (example: “has been eaten”)} ; OR 
   {a single dependent clause (example: “When the dog barked loudly”};) AND (is not a full sentence, or several sentences) AND (is not the title of an entire clause in a Contract) 

3. Identify all arguments made that fit into one of the following categories in the opinion_text:        
       
    A= "an assertion/argument that seeks to promote a specific interpretation of contractual language, rather than trying to establish the rules that should govern the interpretation"; OR
    B= "an assertion/argument about whether or not there exists ambiguity in the existing contractual language"; OR
    C= "an assertion/argument that seeks to establish the rule that should govern the interpretation of contractual language, rather than an assertion/argument that promotes a specific interpretation of the contractual language"; OR
    D= “an assertion/argument that a Locus in a Contract should be interpreted/defined a certain way in order to avoid inconsistencies with other parts of the contract, other contracts between the parties, statutes or the like."
    E= "an assertion/argument regarding the interpretation of contractual language or a Locus in a Contract, but does not fit into any of the categories specified above (A, B, C or D)."

Return all of these arguments in JSON format with the following structure for each <argument>:
{
    "citation": <citation>,
    "disputed_word": <disputed_word>,
    "argument_position": <argument_position>,
    "argument_type": <argument_type>,
    "argument": <argument>,
    "argument_excerpts": <argument_excerpts>,
    "contract_excerpt": <contract_excerpt>
}

Return an array of these JSON objects,

Where:
citation is the given citation for the opinion_text (example of citation: 331 F.Supp.3d 263);
disputed_word (a Locus that is present, word for word, in a  contract between the plaintiff and defendant) AND (must satisfy the definition given in 1. of a Locus) AND (the document that locus belongs to must satisfy the definition given in 2. of a Contract); 
disputed_word should be the specific Locus that is disputed, not the sentence or larger clause that the Locus belongs to.; 
(example of disputed_word: "retirement");
argument_position is either of plaintiff, defendant, or court (example of argument_position: "plaintiff");
argument_type is the type of argument; if the type of argument is either category A, B, C, or D, then argument_type should be "A", "B", "C", or "D"; 
However, if it is of type E, argument_type should be a description akin to the definitions specified above for category A, B, C, and D, specifying exactly what kind of argument regarding the interpretation of contractual language or a Locus in a Contract it is; 
argument is the argument made by argument_position regarding disputed_word of category argument_type;
argument_excerpts should be all of the excerpts from the opinion_text in which the argument is made, combined into a single string; 
contract_excerpt should be the contract clause or sentence within the contract that Locus belongs to; (example of contract_excerpt: “Plaintiffs argue that under the 1997 Plan, participants are eligible for deferred compensation if they retire from any employment at or after age sixty-five, based on the Plan's definition of 'retirement' as 'withdrawal from full time active employment at or after age 65.”);


The same locus may be used in multiple tuples. 
The same argument_position (plaintiff, defendant, court) may make multiple arguments within one opinion_text, that may or may not be of different argument_type.
In this case, return each argument individually, without omitting any arguments made by each position.
If there are no such arguments, return an empty array.
opinion_text: 
"""

context2 = """1. Identify and define Contract to be the legal definition given in the opinion_text; If it is not explicitly provided, a document should be considered a contract
   if the court in the opinion_text deems the document as legally binding.

   2. Define a Locus as (a segment of word(s) that are either: {a single word (example: discuss)} OR {single
   grammatical phrase (noun phrase, verb phrase, adjective phrase, etc.) (example: “has been eaten”)} ; OR 
   {a single dependent clause (example: “When the dog barked loudly”};) AND (is not a full sentence, or several sentences) AND (is not the title of an entire clause in a Contract) 

3. Identify all arguments made that fit into one of the following categories in the opinion_text:        
       
    A= "an assertion/argument that seeks to promote a specific interpretation of contractual language, rather than trying to establish the rules that should govern the interpretation"; OR
    B= "an assertion/argument about whether or not there exists ambiguity in the existing contractual language"; OR
    C= "an assertion/argument that seeks to establish the rule that should govern the interpretation of contractual language, rather than an assertion/argument that promotes a specific interpretation of the contractual language"; OR
    D= “an assertion/argument that a Locus in a Contract should be interpreted/defined a certain way in order to avoid inconsistencies with other parts of the contract, other contracts between the parties, statutes or the like."

Return all of these arguments in JSON format with the following structure for each <argument>:
{
    "citation": <citation>,
    "disputed_word": <disputed_word>,
    "argument_position": <argument_position>,
    "argument_type": <argument_type>,
    "argument": <argument>,
    "argument_excerpts": <argument_excerpts>,
    "contract_excerpt": <contract_excerpt>
}

Return an array of these JSON objects,

Where:
citation is the given citation for the opinion_text (example of citation: 331 F.Supp.3d 263);
disputed_word (a Locus that is present, word for word, in a  contract between the plaintiff and defendant) AND (must satisfy the definition given in 1. of a Locus) AND (the document that locus belongs to must satisfy the definition given in 2. of a Contract); 
disputed_word should be the specific Locus that is disputed, not the sentence or larger clause that the Locus belongs to.; 
(example of disputed_word: "retirement");
argument_position is either of plaintiff, defendant, or court (example of argument_position: "plaintiff");
argument_type is the type of argument (should be "A", "B", "C", or "D");
argument is the argument made by argument_position regarding disputed_word of category argument_type;
argument_excerpts should be all of the excerpts from the opinion_text in which the argument is made, combined into a single string; 
contract_excerpt should be the contract clause or sentence within the contract that Locus belongs to; (example of contract_excerpt: “Plaintiffs argue that under the 1997 Plan, participants are eligible for deferred compensation if they retire from any employment at or after age sixty-five, based on the Plan's definition of 'retirement' as 'withdrawal from full time active employment at or after age 65.”);


The same locus may be used in multiple tuples. 
The same argument_position (plaintiff, defendant, court) may make multiple arguments within one opinion_text, that may or may not be of different argument_type.
In this case, return each argument individually, without omitting any arguments made by each position.
If there are no such arguments, return an empty array.
opinion_text: 
"""

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
    samples = format_csv()
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
