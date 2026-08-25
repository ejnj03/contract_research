from openai import OpenAI
import shelve
import os
import time
import logging

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

context = ""
question_1 = "1. A case that is a contract language interpretation dispute is one where the plaintiff and defendant assert different interpretations of a phrase or term in a contract or argue about whether a phrase or term in a contract is ambiguous and subject to interpretation. Based on this definition, is this case about language interpretation dispute? Answer '1' if it is a contract language interpretation dispute and '0' otherwise."
question_2 = "2. What's the specific word or phrase in the contract that the plaintiff and defendant dispute over? It may be the case that the term or phrase (we call this phrase A) is defined explicitly in the contract, so the dispute is over the interpretation of another term or phrase (we reference this as phrase B) within the part of the contract that defines phrase A. In this case, include only phrase B." 
question_3 = "3. What is the contract excerpt that the disputed phrase or term occurs in? If the answer to the previous question includes two or more terms or phrases, include contract excerpts relevant to both terms or phrases."
question_4 = "4. What's the plaintiff's interpretation of the disputed contract language that was the answer to question 2?"
question_5 = "5. What's the defendant's interpretation of the disputed contract language that was the answer to question 2?"
question_6 = "6. Who did the court side with, and why? Answer 'P' if plaintiff and 'D' if defendant."



def generate_responses(assistant_id):

    message_list = [
                    {"role": "system", "content": context.strip()},
                    {"role": "user", "content": question_1.strip()},
                    {"role": "user", "content": question_2.strip()},
                    {"role": "user", "content": question_3.strip()},
                    {"role": "user", "content": question_4.strip()},
                    {"role": "user", "content": question_5.strip()},
                    {"role": "user", "content": question_6.strip()},
                    #{"role": "user", "content": question_7.strip()},
                ]
    with open('assistant_outputs.jsonl', 'w') as f:
        print(f"processing cases..")
        for text_file in os.listdir('data'):
            print(f"processing case {text_file}")
            message_file = client.files.create(
                file=open(f'data/{text_file}', "rb"), purpose="assistants"
            )
            thread = client.beta.threads.create(
                messages=[
                    {
                    "role": "user",
                    "content": context.strip(),
                    # Attach the new file to the message.
                    "attachments": [
                        { "file_id": message_file.id, "tools": [{"type": "file_search"}]}
                        ]
                    }
                ].extend(message_list)
            )

            run = client.beta.threads.runs.create(
                thread_id = thread.id,
                assistant_id = assistant_id
            )

            while run.status != 'completed':
                time.sleep(0.5)
                run = client.beta.threads.runs.retrieve(thread_id = thread.id, run_id=run.id)
            
            messages = client.beta.threads.messages.list(thread_id = thread.id)
            new_message = messages.data[0].content[0].text.value
            f.write(new_message)
            print(f"writing response: {new_message}")
        f.close()

assistant_id = 'asst_0O6b492evoQBAP0Eoj0cFZ9r'
generate_responses(assistant_id)

            