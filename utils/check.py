import os
from openai import OpenAI
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

if __name__ == '__main__':
    print(client.batches.retrieve("batch_67119f327d108190ab361d84fe0a0270").status)
