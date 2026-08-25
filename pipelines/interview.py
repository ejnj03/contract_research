import vertexai
from vertexai.preview.generative_models import GenerativeModel, ChatSession


import os
from time import sleep
from prompts.qa_questions import context, question_list
from dataset import load_samples

# Vertex AI reads service-account credentials from GOOGLE_APPLICATION_CREDENTIALS.
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "autonomous-star-413714")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
vertexai.init(project=PROJECT_ID, location=LOCATION)

model = GenerativeModel("gemini-1.5-flash-001")



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
    samples = load_samples()
    #print(samples[0])
    for input_sample in samples[5:]:
        chat_session(input_sample["text"], file, input_sample["citation"])
        sleep(30)
        

if __name__ == "__main__":
    process('gemini_output.jsonl')

